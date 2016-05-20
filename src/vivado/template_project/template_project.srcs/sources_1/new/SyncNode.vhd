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
        N_IO     : positive := 1
    )
    port (
        CLK       : in std_logic;
        RST       : in std_logic;
        VALID_IN  : in std_logic;
        READY_IN  : in std_logic;
        SYNC_IN   : in std_logic_vector(WIDTH-1 downto 0);
        VALID_IN_PORT : in std_logic_vector(N_IO-1 downto 0);
        VALID_OUT : out std_logic;
        READY_OUT : out std_logic;
        SYNC_OUT  : out std_logic_vector(WIDTH-1 downto 0)
        );
end SyncNode;

architecture arch of SyncNode is
    signal SyncRE   : std_logic := '0';
begin

    SyncRE <= VALID_IN AND READY_IN;

    FIFO_SYNC_MACRO_inst : FIFO_SYNC_MACRO
    generic map (
        DEVICE => "7SERIES",            -- Target Device: "VIRTEX5, "VIRTEX6", "7SERIES"
        ALMOST_FULL_OFFSET => X"0080",  -- Sets almost full threshold
        ALMOST_EMPTY_OFFSET => X"0080", -- Sets the almost empty threshold
        DATA_WIDTH => 0,   -- Valid values are 1-72 (37-72 only valid when FIFO_SIZE="36Kb")
        FIFO_SIZE => "18Kb")            -- Target BRAM, "18Kb" or "36Kb"
    port map (
        ALMOSTEMPTY => ALMOSTEMPTY,   -- 1-bit output almost empty
        ALMOSTFULL => ALMOSTFULL,     -- 1-bit output almost full
        DO => DO,                     -- Output data, width defined by DATA_WIDTH parameter
        EMPTY => EMPTY,               -- 1-bit output empty
        FULL => FULL,                 -- 1-bit output full
        RDCOUNT => RDCOUNT,           -- Output read count, width determined by FIFO depth
        RDERR => RDERR,               -- 1-bit output read error
        WRCOUNT => WRCOUNT,           -- Output write count, width determined by FIFO depth
        WRERR => WRERR,               -- 1-bit output write error
        CLK => CLK,                   -- 1-bit input clock
        DI => DI,                     -- Input data, width defined by DATA_WIDTH parameter
        RDEN => RDEN,                 -- 1-bit input read enable
        RST => RST,                   -- 1-bit input reset
        WREN => WREN                  -- 1-bit input write enable
    );

end architecture ; -- arch