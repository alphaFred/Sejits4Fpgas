----------------------------------------------------------------------------------
-- Company:
-- Engineer:
--
-- Create Date: 03/21/2016 02:04:20 PM
-- Design Name:
-- Module Name: Convolve_Filter - Behavioral
-- Project Name:
-- Target Devices:
-- Tool Versions:
-- Description:
--
-- Dependencies:
--
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
--
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;

use work.the_filter_package.all;


entity Convolve is
    Generic (
        FILTERMATRIX    : filtMASK      := (0,0,0,0,1,0,0,0,0);
        FILTER_SCALE    : integer       := 1;
        IMG_WIDTH       : positive      := 640;
        IMG_HEIGHT      : positive      := 480;
        IN_BITWIDTH     : positive      := 12;
        OUT_BITWIDTH    : positive      := 16
        );
    Port (
        CLK             : in  std_logic;
        RST             : in  std_logic; -- low active
        VALID_IN        : in  std_logic; -- high active
        DATA_IN         : in  std_logic_vector(IN_BITWIDTH-1 downto 0);
        VALID_OUT       : out std_logic; -- high active
        DATA_OUT        : out std_logic_vector(OUT_BITWIDTH-1 downto 0)
        );
end Convolve;

architecture Behavioral of Convolve is

    -- ======================================================================
    -- COMPONENTS
    -- ======================================================================

    component FILTER is
    generic (
        FILTERMATRIX    : filtMASK      := (0,0,0,0,1,0,0,0,0);
        FILTER_SCALE    : integer       := 1;
        IN_BITWIDTH     : positive      := 12;
        OUT_BITWIDTH    : positive      := 16
    );
    port (
        CLK             : in  std_logic;
        RESET           : in  std_logic;
        IMG_WIDTH       : in  integer   := 1920;
        IMG_HEIGHT      : in  integer   := 1080;
        DATA_IN         : in  std_logic_vector(IN_BITWIDTH-1 downto 0);
        H_SYNC_IN       : in  std_logic;
        V_SYNC_IN       : in  std_logic;
        DATA_OUT        : out std_logic_vector(OUT_BITWIDTH-1 downto 0);
        H_SYNC_OUT      : out std_logic; -- um zwei Takte verzoegert
        V_SYNC_OUT      : out std_logic;
        VALID           : inout std_logic
    );
    end component;

    component STD_FIFO is
        generic (
            constant DATA_WIDTH  : positive := 8;
            constant FIFO_DEPTH : positive := 256
        );
        port (
            CLK     : in  STD_LOGIC;
            RST     : in  STD_LOGIC;
            WriteEn : in  STD_LOGIC;
            DataIn  : in  STD_LOGIC_VECTOR (DATA_WIDTH - 1 downto 0);
            ReadEn  : in  STD_LOGIC;
            DataOut : out STD_LOGIC_VECTOR (DATA_WIDTH - 1 downto 0);
            Empty   : out STD_LOGIC;
            Full    : out STD_LOGIC
        );
    end component;

    -- ======================================================================
    -- SIGNALS | CONSTANTS
    -- ======================================================================

    signal ipt_fifo_ren     :   std_logic := '0';
    signal ipt_fifo_ren_ctrl:   std_logic := '0';
    signal ipt_fifo_wen     :   std_logic := '0';
    signal ipt_fifo_wen_ctrl:   std_logic := '0';
    signal ipt_fifo_out     :   std_logic_vector(7 downto 0);
    signal ipt_fifo_empty   :   std_logic;
    signal ipt_fifo_full    :   std_logic;

    signal opt_fifo_rst     :   std_logic := '0';
    signal opt_fifo_ren     :   std_logic := '0';
    signal opt_fifo_wen     :   std_logic := '0';
    signal opt_fifo_in      :   std_logic_vector(7 downto 0);
    signal opt_fifo_in_reg  :   std_logic_vector(7 downto 0);
    signal opt_fifo_out     :   std_logic_vector(7 downto 0);
    signal opt_fifo_full    :   std_logic;
    signal opt_fifo_empty   :   std_logic;

    signal filter_rst       :   std_logic := '0';
    signal filter_hsync     :   std_logic := '0';
    signal filter_vsync     :   std_logic := '0';
    signal filter_valid_out :   std_logic;
    signal filter_finished  :   std_logic := '0';

    signal hsync_out        :   std_logic;
    signal vsync_out        :   std_logic;

    -- ======================================================================
    -- FSM PARAMETERS
    -- ======================================================================

    signal ipt_fifo_active  : std_logic := '0';

    -- INPUT FIFO
    type inputFIFO_type is ( IPT_FIFO_IDLE, IPT_FIFO_LOAD, IPT_FIFO_INIT, IPT_FIFO_WORK);
    signal inputFIFO_state : inputFIFO_type := IPT_FIFO_IDLE;
    constant ipt_fifo_lct   :   integer := 500; -- load count
    signal   ipt_fifo_lctr  :   integer := 0; -- load counter

    type FILTER_type is ( FILTER_IDLE, FILTER_INIT, FILTER_WORK, FILTER_STALL, FILTER_END_IMG);
    signal FILTER_state : FILTER_type := FILTER_IDLE;
    constant filter_i_ct  : integer := 2; -- filter init count
    signal filter_i_ctr   : integer := 0; -- filter init counter
    signal filter_w_ctr     :   integer := 0; -- filter width counter
    signal filter_h_ctr     :   integer := 0; -- filter height counter
    constant filter_stall_ct:   integer := 2; -- filter stall count
    signal filter_stall_ctr :   integer := 0; -- filter stall counter

    type outputFIFO_type is ( OPT_FIFO_IDLE, OPT_FIFO_LOAD, OPT_FIFO_INIT, OPT_FIFO_WORK, OPT_FIFO_FINISH);
    signal outputFIFO_state : outputFIFO_type := OPT_FIFO_IDLE;
    constant opt_fifo_lct   :   integer := 10000; -- load count
    signal   opt_fifo_lctr  :   integer := 0; -- load counter
begin
    -- ======================================================================
    -- COMPONENTS
    -- ======================================================================
    input_fifo : component STD_FIFO
    generic map (
        DATA_WIDTH => 8,
        FIFO_DEPTH => 20000
    )
    port map (
        CLK => CLK,
        RST => not RST,
        WriteEn => VALID_IN or ipt_fifo_wen_ctrl,
        DataIn => DATA_IN,
        ReadEn => ipt_fifo_ren or ipt_fifo_ren_ctrl,
        DataOut => ipt_fifo_out,
        Empty => ipt_fifo_empty,
        Full => ipt_fifo_full
    );

    filter_unit : FILTER
    generic map (
        FILTERMATRIX    => FILTERMATRIX,
        FILTER_SCALE    => FILTER_SCALE,
        IN_BITWIDTH     => IN_BITWIDTH,
        OUT_BITWIDTH    => OUT_BITWIDTH
    )
    port map (
        CLK => CLK,
        RESET => not filter_rst,
        IMG_WIDTH => 640,
        IMG_HEIGHT => 480,
        DATA_IN => ipt_fifo_out,
        H_SYNC_IN => filter_hsync,
        V_SYNC_IN => filter_vsync,
        DATA_OUT => opt_fifo_in,
        H_SYNC_OUT => hsync_out,
        V_SYNC_OUT => vsync_out,
        VALID => filter_valid_out
    );

    -- VALID_OUT <= filter_valid_out;

    output_fifo : component STD_FIFO
    generic map (
        DATA_WIDTH => 8,
        FIFO_DEPTH => 20000
    )
    port map (
        CLK => CLK,
        RST => NOT RST,
        WriteEn => filter_valid_out,
        DataIn => opt_fifo_in,
        ReadEn => opt_fifo_ren,
        DataOut => DATA_OUT,
        Empty => opt_fifo_empty,
        Full => opt_fifo_full
    );

    -- ======================================================================
    -- PROCESSES
    -- ======================================================================
    INPUT_FIFO_FSM : process( CLK )
    begin
        if RST = '0' then
            ipt_fifo_active <= '0';
            ipt_fifo_wen <= '0';

        elsif(rising_edge(CLK)) then
            case inputFIFO_state is
                when IPT_FIFO_IDLE =>
                    -- wait for valid input data
                    ipt_fifo_active <= '0';

                    if VALID_IN = '1' then
                        inputFIFO_state <= IPT_FIFO_LOAD;
                    else
                        inputFIFO_state <= IPT_FIFO_IDLE;
                    end if;

                when IPT_FIFO_LOAD =>
                    -- buffer data to ensure valid output every clk cycle
                    if ipt_fifo_lctr = ipt_fifo_lct then
                        ipt_fifo_lctr <= 0;
                        inputFIFO_state <= IPT_FIFO_INIT;
                    else
                        ipt_fifo_lctr <= ipt_fifo_lctr + 1;
                        inputFIFO_state <= IPT_FIFO_LOAD;
                    end if;

                when IPT_FIFO_INIT =>
                    -- cycle read once to get valid data in output signal
                    if ipt_fifo_ren = '1' then
                        ipt_fifo_ren <= '0';
                        inputFIFO_state <= IPT_FIFO_WORK;
                    else
                        ipt_fifo_ren <= '1';
                        inputFIFO_state <= IPT_FIFO_INIT;
                    end if;

                when IPT_FIFO_WORK =>
                    -- read data ever clk cycle
                    ipt_fifo_active <= '1';
                    inputFIFO_state <= IPT_FIFO_WORK;

                when others =>
            end case;
        end if;
    end process; -- INPUT_FIFO_FSM

    FILTER_FSM : process( CLK )
    begin
        if RST = '0' then

        elsif(rising_edge(CLK)) then
            case FILTER_state is
                when FILTER_IDLE =>
                    if ipt_fifo_active = '1' then
                        FILTER_state <= FILTER_INIT;
                    else
                        FILTER_state <= FILTER_IDLE;
                    end if;

                when FILTER_INIT =>
                    filter_rst <= '1';
                    if filter_i_ctr = filter_i_ct then
                        FILTER_state <= FILTER_WORK;
                    else
                        filter_i_ctr <= filter_i_ctr + 1;
                        FILTER_state <= FILTER_INIT;
                    end if;

                when FILTER_WORK =>
                    ipt_fifo_ren_ctrl <= '1';
                    filter_hsync <= '1';
                    filter_vsync <= '1';

                    filter_w_ctr <= filter_w_ctr + 1;

                    if filter_w_ctr = IMG_WIDTH then
                        filter_hsync <= '0';
                        ipt_fifo_ren_ctrl <= '0';
                        filter_h_ctr <= filter_h_ctr + 1;
                        FILTER_state <= FILTER_STALL;
                    else
                        FILTER_state <= FILTER_WORK;
                    end if;

                when FILTER_STALL =>
                    filter_w_ctr <= 0;
                    -- ipt_fifo_ren_ctrl <= '0';
                    if filter_stall_ctr < filter_stall_ct then
                        filter_stall_ctr <= filter_stall_ctr + 1;
                    else
                        filter_stall_ctr <= 0;
                    end if;

                    if filter_h_ctr = IMG_HEIGHT then
                        filter_finished <= '1';
                        filter_vsync <= '0';
                        FILTER_state <= FILTER_END_IMG;
                    elsif filter_stall_ctr = filter_stall_ct then
                        FILTER_state <= FILTER_WORK;
                    else
                        FILTER_state <= FILTER_STALL;
                    end if;

                when FILTER_END_IMG =>

                when others =>
            end case;
        end if;
    end process; -- FILTER_FSM

    DATA_REG_PROC : process (CLK)
    begin
        if RST = '0' then

        elsif rising_edge(CLK) then
            opt_fifo_in_reg <= opt_fifo_in;
        end if;
    end process; -- DATA_REG_PROC

    OUTPUT_FIFO_FSM : process( CLK )
    begin
        if RST = '0' then

        elsif(rising_edge(CLK)) then
            case outputFIFO_state is
                when OPT_FIFO_IDLE =>
                    -- wait for valid input data
                    if filter_valid_out = '1' then
                        opt_fifo_rst <= '1';
                        opt_fifo_wen <= '1';
                        outputFIFO_state <= OPT_FIFO_LOAD;
                    else
                        opt_fifo_rst <= '0';
                        opt_fifo_wen <= '0';
                        outputFIFO_state <= OPT_FIFO_IDLE;
                    end if;
                when OPT_FIFO_LOAD =>
                    -- buffer data to ensure valid output every clk cycle
                    if opt_fifo_lctr = opt_fifo_lct then
                        opt_fifo_lctr <= 0;
                        outputFIFO_state <= OPT_FIFO_INIT;
                    else
                        opt_fifo_lctr <= opt_fifo_lctr + 1;
                        outputFIFO_state <= OPT_FIFO_LOAD;
                    end if;

                when OPT_FIFO_INIT =>
                    -- cycle read once to get valid data in output signal
                    if opt_fifo_ren = '1' then
                        opt_fifo_ren <= '0';
                        outputFIFO_state <= OPT_FIFO_WORK;
                    else
                        opt_fifo_ren <= '1';
                        outputFIFO_state <= OPT_FIFO_INIT;
                    end if;

                when OPT_FIFO_WORK =>
                    -- read data ever clk cycle
                    opt_fifo_ren <= '1';
                    VALID_OUT <= '1';
                    outputFIFO_state <= OPT_FIFO_WORK;

                    if filter_finished = '1' and filter_valid_out = '0' then
                        opt_fifo_wen <= '0';
                        outputFIFO_state <= OPT_FIFO_FINISH;
                    else
                        opt_fifo_wen <= '1';
                    end if;

                when OPT_FIFO_FINISH =>
                    if opt_fifo_empty = '0' then
                        opt_fifo_ren <= '1';
                        outputFIFO_state <= OPT_FIFO_FINISH;
                    else
                        opt_fifo_ren <= '0';
                        VALID_OUT <= '0';
                        outputFIFO_state <= OPT_FIFO_IDLE;
                    end if;

            end case;
        end if;
    end process ; -- OUTPUT_FIFO_FSM
end Behavioral;

