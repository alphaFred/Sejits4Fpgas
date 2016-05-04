library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNIMACRO;
use UNIMACRO.vcomponents.all;

Library UNISIM;
use UNISIM.vcomponents.all;


entity SubBB is
    port (
        CLK       : in std_logic;
        RST       : in std_logic;
        VALID_IN  : in std_logic;
        LEFT      : in std_logic_vector(31 downto 0);
        RIGHT     : in std_logic_vector(31 downto 0);
        VALID_OUT : out std_logic;
        SUB_OUT   : out std_logic_vector(31 downto 0)
        );
end SubBB;

architecture arch of SubBB is
    signal RESULT :std_logic_vector(31 downto 0);
    -- END      DSP48E1_inst_1
    constant DELAY_ADD_SUB : positive := 2;
    --
    TYPE iBus_ADD_SUB is array(DELAY_ADD_SUB-1 downto 0) of std_logic;
    --
    signal ValidsRegBus_ADD_SUB : iBus_ADD_SUB := (others => '0');
    --
    COMPONENT logic_dff_block
    Port (
        D   : in STD_LOGIC;
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        Q   : out STD_LOGIC
    );
    END COMPONENT;
begin
    ADDSUB_MACRO_inst : ADDSUB_MACRO
    generic map (
        DEVICE => "7SERIES", -- Target Device: "VIRTEX5", "7SERIES", "SPARTAN6"
        LATENCY => 2,        -- Desired clock cycle latency, 0-2
        WIDTH => 32)         -- Input / Output bus width, 1-48
    port map (
        CARRYOUT => open, -- 1-bit carry-out output signal
        RESULT => RESULT,     -- Add/sub result output, width defined by WIDTH generic
        A => LEFT,               -- Input A bus, width defined by WIDTH generic
        ADD_SUB => '0',   -- 1-bit add/sub input, high selects add, low selects subtract
        B => RIGHT,               -- Input B bus, width defined by WIDTH generic
        CARRYIN => '0',   -- 1-bit carry-in input
        CE => '1',             -- 1-bit clock enable input
        CLK =>CLK,           -- 1-bit clock input
        RST => RST            -- 1-bit active high synchronous reset
    );

    validReg_SUB_int: for i in 0 to DELAY_ADD_SUB generate
    begin
        validdffLeft_SUB: if i = 0 generate
        begin
            valid_dff: component logic_dff_block
                port map (
                    D => VALID_IN,
                    CLK => CLK,
                    RST => RST,
                    Q => ValidsRegBus_ADD_SUB(i)
                );
        end generate validdffLeft_SUB;
        --
        dffOthers_SUB: if (i > 0 AND i < DELAY_ADD_SUB) generate
        begin
            valid_dff: component logic_dff_block
                port map (
                    D => ValidsRegBus_ADD_SUB(i-1),
                    CLK => CLK,
                    RST => RST,
                    Q => ValidsRegBus_ADD_SUB(i)
                );
        end generate dffOthers_SUB;
        --
        dffRight_SUB: if i = DELAY_ADD_SUB generate
        begin
            valid_dff: component logic_dff_block
                port map (
                    D => ValidsRegBus_ADD_SUB(i-1),
                    CLK => CLK,
                    RST => RST,
                    Q => VALID_OUT
                );
        end generate dffRight_SUB;
    end generate validReg_SUB_int;

    calc_result : process(clk)
    begin
        if rising_edge(clk) then
            SUB_OUT <= RESULT;
        end if;
    end process;
end architecture ; -- arch
