----------------------------------------------------------------------------------
-- Company:
-- Engineer:
--
-- Create Date: 03/21/2016 02:04:20 PM
-- Design Name:
-- Module Name: Convolve - Behavioral
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

library xil_defaultlib;
use xil_defaultlib.filter_input_fifo_1;

use work.the_filter_package.all;


entity Convolve is
    Generic (
        FILTERMATRIX    : filtMASK      := (0,0,0,0,1,0,0,0,0);
        FILTER_SCALE    : integer       := 1;
        IMG_WIDTH       : positive      := 640;
        IMG_HEIGHT      : positive      := 480
        );
    Port (
        CLK             : in  std_logic;
        RST             : in  std_logic; -- low active
        VALID_IN        : in  std_logic; -- high active
        READY_IN        : in  std_logic;
        DATA_IN         : in  std_logic_vector(31 downto 0);
        VALID_OUT       : out std_logic; -- high active
        READY_OUT       : out std_logic;
        DATA_OUT        : out std_logic_vector(31 downto 0)
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

    component filter_input_fifo_1 is
    port (
        clk : IN STD_LOGIC;
        rst : IN STD_LOGIC;
        din : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
        wr_en : IN STD_LOGIC;
        rd_en : IN STD_LOGIC;
        dout : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
        full : OUT STD_LOGIC;
        empty : OUT STD_LOGIC;
        data_count : OUT STD_LOGIC_VECTOR(11 DOWNTO 0)
        );
    end component;

    -- ======================================================================
    -- SIGNALS | CONSTANTS
    -- ======================================================================
    signal ipt_fifo_ren     :   std_logic := '0';
    signal ipt_fifo_full    :   std_logic;
    signal input_fifo_rst   :   std_logic := '0';
    signal ipt_fifo_out     :   std_logic_vector(31 downto 0);
    signal ipt_fifo_data_count : std_logic_vector(11 DOWNTO 0);

    signal filter_hsync     :   std_logic := '0';
    signal filter_vsync     :   std_logic := '0';
    signal filter_valid     :   std_logic;
    signal filter_data_out  :   std_logic_vector(15 downto 0);

    -- ======================================================================
    -- FSM PARAMETERS
    -- ======================================================================

    type FILTER_type is ( FILTER_IDLE, FILTER_WORK, FILTER_STALL, FILTER_NLINE, FILTER_NIMG);
    signal FILTER_state : FILTER_type := FILTER_IDLE;
    signal filter_w_ctr     :   integer := 0; -- filter width counter
    signal filter_h_ctr     :   integer := 0; -- filter height counter

begin
    -- ======================================================================
    -- COMPONENTS
    -- ======================================================================
    input_fifo : component filter_input_fifo_1
    port map(
        clk => CLK,
        rst => RST or input_fifo_rst,
        din => DATA_IN,
        wr_en => VALID_IN,
        rd_en => ipt_fifo_ren,
        dout => ipt_fifo_out,
        full => ipt_fifo_full,
        empty => open,
        data_count => ipt_fifo_data_count
    );

    READY_OUT <= NOT ipt_fifo_full AND READY_IN;

    filter_unit : filter
    generic map (
        FILTERMATRIX    => FILTERMATRIX,
        FILTER_SCALE    => FILTER_SCALE,
        IN_BITWIDTH     => 12,
        OUT_BITWIDTH    => 16
    )
    port map (
        CLK => CLK,
        RESET => RST,
        IMG_WIDTH => IMG_WIDTH,
        IMG_HEIGHT => IMG_HEIGHT,
        DATA_IN => ipt_fifo_out(11 downto 0),
        H_SYNC_IN => filter_hsync,
        V_SYNC_IN => filter_vsync,
        DATA_OUT => filter_data_out,
        H_SYNC_OUT => open,
        V_SYNC_OUT => open,
        VALID => filter_valid
    );
    DATA_OUT <= (31 downto 16 => '0') & filter_data_out;
    VALID_OUT <= filter_valid;

    -- ======================================================================
    -- PROCESSES
    -- ======================================================================

    FILTER_FSM : process( CLK )
    begin
        if RST = '1' then
            FILTER_state <= FILTER_IDLE;
            filter_hsync <= '0';
            filter_vsync <= '0';
            ipt_fifo_ren <= '0';
            filter_w_ctr <= 0;
            filter_h_ctr <= 0;
        elsif(rising_edge(CLK)) then
            case FILTER_state is
                when FILTER_IDLE =>
                    input_fifo_rst <= '0';
                    filter_hsync <= '0';
                    filter_vsync <= '0';
                    --
                    if unsigned(ipt_fifo_data_count) >= IMG_WIDTH then
                        FILTER_state <= FILTER_WORK;
                    else
                        FILTER_state <= FILTER_IDLE;
                    end if;

                when FILTER_WORK =>
                    ipt_fifo_ren <= '1';

                    filter_hsync <= '1';
                    filter_vsync <= '1';

                    filter_w_ctr <= filter_w_ctr + 1;
                    if filter_w_ctr = IMG_WIDTH then
                        filter_hsync <= '0';
                        ipt_fifo_ren <= '0';
                        filter_h_ctr <= filter_h_ctr + 1;
                        FILTER_state <= FILTER_STALL;
                    else
                        FILTER_state <= FILTER_WORK;
                    end if;

                when FILTER_STALL =>
                    filter_w_ctr <= 0;

                    if filter_h_ctr = IMG_HEIGHT then
                        filter_vsync <= '0';
                        filter_h_ctr <= 0;
                        FILTER_state <= FILTER_NIMG;
                    else
                        FILTER_state <= FILTER_NLINE;
                    end if;

                when FILTER_NLINE =>
                    if unsigned(ipt_fifo_data_count) >= IMG_WIDTH then
                        FILTER_state <= FILTER_WORK;
                    else
                        FILTER_state <= FILTER_NLINE;
                    end if;

                when FILTER_NIMG =>
                    input_fifo_rst <= '1';
                    FILTER_state <= FILTER_IDLE;

                when others =>
            end case;
        end if;
    end process; -- FILTER_FSM
end Behavioral;

