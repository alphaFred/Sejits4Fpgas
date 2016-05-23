library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNIMACRO;
use UNIMACRO.vcomponents.all;

Library UNISIM;
use UNISIM.vcomponents.all;


-- All connected input streams must have the same width!
-- Input stream width = WIDTH/N_IO
entity SyncNode is
    generic (
        WIDTH    : positive := 32;
        N_IO     : positive := 2;
        DELAY    : positive := 1
    );
    port (
        CLK       : in std_logic;
        RST       : in std_logic;
        VALID_IN  : in std_logic;
        READY_IN  : in std_logic;
        SYNC_IN   : in std_logic_vector((N_IO*WIDTH)-1 downto 0);
        VALID_IN_PORT : in std_logic_vector(N_IO-1 downto 0);
        VALID_OUT : out std_logic;
        READY_OUT : out std_logic;
        SYNC_OUT  : out std_logic_vector((N_IO*WIDTH)-1 downto 0)
        );
end SyncNode;

architecture arch of SyncNode is
    signal SyncRE   : std_logic := '0';
    -- Width of RDCOUNT/WRCOUNT is not generic to input!!
    signal RDCOUNT  : std_logic_vector(17 downto 0);
    signal WRCOUNT  : std_logic_vector(17 downto 0);
    --
    signal ALMOSTEMPTY_log : std_logic_vector(N_IO-1 downto 0);
    signal ALMOSTFULL_log : std_logic_vector(N_IO-1 downto 0);
    signal EMPTY_log    : std_logic_vector(N_IO-1 downto 0);
    signal FULL_log     : std_logic_vector(N_IO-1 downto 0);
    --
    TYPE READ_D is array(2 downto 0) of std_logic;
    signal read_delay : READ_D;
    TYPE iBus_D is array(N_IO-1 downto 0) of std_logic_vector(WIDTH-1 downto 0);
    signal data_in : iBus_D;
    signal data_out : iBus_D;
    --
    component sync_fifo_32x64 is
    port (
        clk : IN STD_LOGIC;
        rst : IN STD_LOGIC;
        din : IN STD_LOGIC_VECTOR(31 DOWNTO 0);
        wr_en : IN STD_LOGIC;
        rd_en : IN STD_LOGIC;
        dout : OUT STD_LOGIC_VECTOR(31 DOWNTO 0);
        full : OUT STD_LOGIC;
        empty : OUT STD_LOGIC
        );
    end component;
begin

    -- SyncRE <= VALID_IN AND READY_IN;

    data_in(0) <= SYNC_IN(31 downto 0);
    data_in(1) <= SYNC_IN(63 downto 32);

    SYNC_OUT(31 downto 0) <= data_out(0);
    SYNC_OUT(63 downto 32) <= data_out(1);

    fifos: for i in 0 to N_IO-1 generate
    begin
        sync_fifo_inst : component sync_fifo_32x64
        port map(
            clk => CLK,
            rst => RST,
            din => data_in(i),
            wr_en => VALID_IN_PORT(i),
            rd_en => SyncRE,
            dout => data_out(i),
            full => FULL_log(i),
            empty => EMPTY_log(i)
        );
    end generate fifos;

    re_delay : process(CLK)
    begin
        if CLK'event and CLK='1' then
            SyncRE <= read_delay(1);
            read_delay(1) <= read_delay(0);
            read_delay(0) <= VALID_IN AND READY_IN;
        end if;
    end process;

    READY_OUT <= READY_IN;
    VALID_OUT <= SyncRE;
end architecture ; -- arch
