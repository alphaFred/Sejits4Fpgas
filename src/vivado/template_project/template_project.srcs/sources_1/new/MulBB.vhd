----------------------------------------------------------------------------------
-- Company:
-- Engineer:
--
-- Create Date: 07/29/2015 11:08:18 AM
-- Design Name:
-- Module Name: dsp_32x32Mul_block - Behavioral
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

library UNIMACRO;
use UNIMACRO.vcomponents.all;

Library UNISIM;
use UNISIM.vcomponents.all;


entity MulBB is
    port (
        CLK       : in std_logic;
        RST       : in std_logic;
        VALID_IN  : in std_logic;
        LEFT      : in std_logic_vector(31 downto 0);
        RIGHT     : in std_logic_vector(31 downto 0);
        VALID_OUT : out std_logic;
        MUL_OUT   : out std_logic_vector(31 downto 0)
        );
end MulBB;

architecture Behavioral of MulBB is

    signal A_INPUT : std_logic_vector(41 downto 0) := (others => '0');
    signal B_INPUT : std_logic_vector(34 downto 0) := (others => '0');
    signal P_OUTPUT : std_logic_vector(75 downto 0) := (others => '0');

-- BEGIN    DSP48E1_inst_4
    signal MULTISIGNOUT_DSP4 : std_logic := '0';
    signal CARRYCASCOUT_DSP4 : std_logic := '0';

    signal OVERFLOW_DSP4 : std_logic := '0';
    signal PATTERNBDETECT_DSP4 : std_logic := '0';
    signal PATTERNDETECT_DSP4 : std_logic := '0';
    signal UNDERFLOW_DSP4 : std_logic := '0';
    --
    signal P_DSP4 : std_logic_vector(47 downto 0) := (others => '0');
    --
    signal ACIN_DSP4 : std_logic_vector(29 downto 0) := (others => '0');
    signal BCIN_DSP4 : std_logic_vector(17 downto 0) := (others => '0');
    signal CARRYCASCIN_DSP4 : std_logic := '0';
    signal MULTISIGNIN_DSP4 : std_logic := '0';
    signal PCIN_DSP4 : std_logic_vector(47 downto 0) := (others => '0');
    signal PCOUT_DSP4 : std_logic_vector(47 downto 0) := (others => '0');
    --
    signal ALUMODE_DSP4 : std_logic_vector(3 downto 0) := (others => '0');
    signal CARRYINSEL_DSP4 : std_logic_vector(2 downto 0) := (others => '0');
    signal INMODE_DSP4 : std_logic_vector(4 downto 0) := (others => '0');
    signal OPMODE_DSP4 : std_logic_vector(6 downto 0) := (others => '0');
    --
    signal A_DSP4 : std_logic_vector(29 downto 0) := (others => '0');
    signal B_DSP4 : std_logic_vector(17 downto 0) := (others => '0');
    signal C_DSP4 : std_logic_vector(47 downto 0) := (others => '0');
    signal CARRYIN_DSP4 : std_logic := '0';
    signal D_DSP4 : std_logic_vector(24 downto 0) := (others => '0');
-- END      DSP48E1_inst_4

-- BEGIN    DSP48E1_inst_3
    signal MULTISIGNOUT_DSP3 : std_logic := '0';
    signal CARRYCASCOUT_DSP3 : std_logic := '0';

    signal OVERFLOW_DSP3 : std_logic := '0';
    signal PATTERNBDETECT_DSP3 : std_logic := '0';
    signal PATTERNDETECT_DSP3 : std_logic := '0';
    signal UNDERFLOW_DSP3 : std_logic := '0';
    --
    signal P_DSP3 : std_logic_vector(47 downto 0) := (others => '0');
    --
    signal ACIN_DSP3 : std_logic_vector(29 downto 0) := (others => '0');
    signal BCIN_DSP3 : std_logic_vector(17 downto 0) := (others => '0');

    signal ACOUT_DSP3 : std_logic_vector(29 downto 0) := (others => '0');
    signal BCOUT_DSP3 : std_logic_vector(17 downto 0) := (others => '0');

    signal CARRYCASCIN_DSP3 : std_logic := '0';
    signal MULTISIGNIN_DSP3 : std_logic := '0';
    signal PCIN_DSP3 : std_logic_vector(47 downto 0) := (others => '0');
    signal PCOUT_DSP3 : std_logic_vector(47 downto 0) := (others => '0');
    --
    signal ALUMODE_DSP3 : std_logic_vector(3 downto 0) := (others => '0');
    signal CARRYINSEL_DSP3 : std_logic_vector(2 downto 0) := (others => '0');
    signal INMODE_DSP3 : std_logic_vector(4 downto 0) := (others => '0');
    signal OPMODE_DSP3 : std_logic_vector(6 downto 0) := (others => '0');
    --
    signal A_DSP3 : std_logic_vector(29 downto 0) := (others => '0');
    signal B_DSP3 : std_logic_vector(17 downto 0) := (others => '0');
    signal C_DSP3 : std_logic_vector(47 downto 0) := (others => '0');
    signal CARRYIN_DSP3 : std_logic := '0';
    signal D_DSP3 : std_logic_vector(24 downto 0) := (others => '0');
-- END      DSP48E1_inst_3

-- BEGIN    DSP48E1_inst_2
    signal MULTISIGNOUT_DSP2 : std_logic := '0';
    signal CARRYCASCOUT_DSP2 : std_logic := '0';

    signal OVERFLOW_DSP2 : std_logic := '0';
    signal PATTERNBDETECT_DSP2 : std_logic := '0';
    signal PATTERNDETECT_DSP2 : std_logic := '0';
    signal UNDERFLOW_DSP2 : std_logic := '0';
    --
    signal P_DSP2 : std_logic_vector(47 downto 0) := (others => '0');
    --
    signal ACIN_DSP2 : std_logic_vector(29 downto 0) := (others => '0');
    signal BCIN_DSP2 : std_logic_vector(17 downto 0) := (others => '0');

    signal ACOUT_DSP2 : std_logic_vector(29 downto 0) := (others => '0');
    signal BCOUT_DSP2 : std_logic_vector(17 downto 0) := (others => '0');

    signal CARRYCASCIN_DSP2 : std_logic := '0';
    signal MULTISIGNIN_DSP2 : std_logic := '0';
    signal PCIN_DSP2 : std_logic_vector(47 downto 0) := (others => '0');
    signal PCOUT_DSP2 : std_logic_vector(47 downto 0) := (others => '0');
    --
    signal ALUMODE_DSP2 : std_logic_vector(3 downto 0) := (others => '0');
    signal CARRYINSEL_DSP2 : std_logic_vector(2 downto 0) := (others => '0');
    signal INMODE_DSP2 : std_logic_vector(4 downto 0) := (others => '0');
    signal OPMODE_DSP2 : std_logic_vector(6 downto 0) := (others => '0');
    --
    signal A_DSP2 : std_logic_vector(29 downto 0) := (others => '0');
    signal B_DSP2 : std_logic_vector(17 downto 0) := (others => '0');
    signal C_DSP2 : std_logic_vector(47 downto 0) := (others => '0');
    signal CARRYIN_DSP2 : std_logic := '0';
    signal D_DSP2 : std_logic_vector(24 downto 0) := (others => '0');
-- END      DSP48E1_inst_2

-- BEGIN    DSP48E1_inst_1
    signal MULTISIGNOUT_DSP1 : std_logic := '0';
    signal CARRYCASCOUT_DSP1 : std_logic := '0';

    signal OVERFLOW_DSP1 : std_logic := '0';
    signal PATTERNBDETECT_DSP1 : std_logic := '0';
    signal PATTERNDETECT_DSP1 : std_logic := '0';
    signal UNDERFLOW_DSP1 : std_logic := '0';
    --
    signal P_DSP1 : std_logic_vector(47 downto 0) := (others => '0');
    --
    signal ACIN_DSP1 : std_logic_vector(29 downto 0) := (others => '0');
    signal BCIN_DSP1 : std_logic_vector(17 downto 0) := (others => '0');

    signal ACOUT_DSP1 : std_logic_vector(29 downto 0) := (others => '0');
    signal BCOUT_DSP1 : std_logic_vector(17 downto 0) := (others => '0');

    signal CARRYCASCIN_DSP1 : std_logic := '0';
    signal MULTISIGNIN_DSP1 : std_logic := '0';
    signal PCIN_DSP1 : std_logic_vector(47 downto 0) := (others => '0');
    signal PCOUT_DSP1 : std_logic_vector(47 downto 0) := (others => '0');
    --
    signal ALUMODE_DSP1 : std_logic_vector(3 downto 0) := (others => '0');
    signal CARRYINSEL_DSP1 : std_logic_vector(2 downto 0) := (others => '0');
    signal INMODE_DSP1 : std_logic_vector(4 downto 0) := (others => '0');
    signal OPMODE_DSP1 : std_logic_vector(6 downto 0) := (others => '0');
    --
    signal A_DSP1 : std_logic_vector(29 downto 0) := (others => '0');
    signal B_DSP1 : std_logic_vector(17 downto 0) := (others => '0');
    signal C_DSP1 : std_logic_vector(47 downto 0) := (others => '0');
    signal CARRYIN_DSP1 : std_logic := '0';
    signal D_DSP1 : std_logic_vector(24 downto 0) := (others => '0');
-- END      DSP48E1_inst_1

COMPONENT dsp_sreg_block
    Generic (
        WIDTH   : natural;
        LENGTH  : natural
    );
    Port (
        D   : in STD_LOGIC_VECTOR (WIDTH-1 downto 0);
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        Q   : out STD_LOGIC_VECTOR (WIDTH-1 downto 0)
    );
END COMPONENT;

COMPONENT dsp_dff_block
    Generic (
        Width   : natural
    );
    Port (
        D : in STD_LOGIC_VECTOR (WIDTH-1 downto 0);
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        Q : out STD_LOGIC_VECTOR (WIDTH-1 downto 0)
    );
END COMPONENT;
begin

--  DSP_4   OPMODE: 1010101 (shift PCIN | M | M)
--   ^
--   |
--  DSP_3   OPMODE: 0010101 (PCIN | M | M)
--   ^
--   |
--  DSP_2   OPMODE: 1010101 (shift PCIN | M | M)
--   ^
--   |
--  DSP_1   OPMODE: 0000101 (0 | M | M)


-- ############################################################################

DSP48E1_inst_4 : DSP48E1
generic map (
    -- Feature Control Attributes: Data Path Selection
    A_INPUT             => "DIRECT",               -- Selects A input source, "DIRECT" (A port) or "CASCADE" (ACIN port)
    B_INPUT             => "CASCADE",               -- Selects B input source, "DIRECT" (B port) or "CASCADE" (BCIN port)
    USE_DPORT           => FALSE,                -- Select D port usage (TRUE or FALSE)
    USE_MULT            => "MULTIPLY",            -- Select multiplier usage ("MULTIPLY", "DYNAMIC", or "NONE")
    USE_SIMD            => "ONE48",               -- SIMD selection ("ONE48", "TWO24", "FOUR12")
    -- Pattern Detector Attributes: Pattern Detection Configuration
    AUTORESET_PATDET    => "NO_RESET",    -- "NO_RESET", "RESET_MATCH", "RESET_NOT_MATCH"
    MASK                => X"3fffffffffff",           -- 48-bit mask value for pattern detect (1=ignore)
    PATTERN             => X"000000000000",        -- 48-bit pattern match for pattern detect
    SEL_MASK            => "MASK",                -- "C", "MASK", "ROUNDING_MODE1", "ROUNDING_MODE2"
    SEL_PATTERN         => "PATTERN",          -- Select pattern value ("PATTERN" or "C")
    USE_PATTERN_DETECT  => "NO_PATDET",         -- Enable pattern detect ("PATDET" or "NO_PATDET")
    -- Register Control Attributes: Pipeline Register Configuration
    ACASCREG            => 1,                     -- Number of pipeline stages between A/ACIN and ACOUT (0, 1 or 2)
    ADREG               => 1,                        -- Number of pipeline stages for pre-adder (0 or 1)
    ALUMODEREG          => 1,                   -- Number of pipeline stages for ALUMODE (0 or 1)
    AREG                => 1,                         -- Number of pipeline stages for A (0, 1 or 2)
    BCASCREG            => 1,                     -- Number of pipeline stages between B/BCIN and BCOUT (0, 1 or 2)
    BREG                => 1,                         -- Number of pipeline stages for B (0, 1 or 2)
    CARRYINREG          => 1,                   -- Number of pipeline stages for CARRYIN (0 or 1)
    CARRYINSELREG       => 1,                -- Number of pipeline stages for CARRYINSEL (0 or 1)
    CREG                => 1,                         -- Number of pipeline stages for C (0 or 1)
    DREG                => 1,                         -- Number of pipeline stages for D (0 or 1)
    INMODEREG           => 1,                    -- Number of pipeline stages for INMODE (0 or 1)
    MREG                => 1,                         -- Number of multiplier pipeline stages (0 or 1)
    OPMODEREG           => 1,                    -- Number of pipeline stages for OPMODE (0 or 1)
    PREG                => 1                          -- Number of pipeline stages for P (0 or 1)
    )
port map (
    -- Cascade: 30-bit (each) output: Cascade Ports
    ACOUT               => open,                   -- 30-bit output: A port cascade output
    BCOUT               => open,                   -- 18-bit output: B port cascade output
    CARRYCASCOUT        => CARRYCASCOUT_DSP4,     -- 1-bit output: Cascade carry output
    MULTSIGNOUT         => MULTISIGNOUT_DSP4,       -- 1-bit output: Multiplier sign cascade output
    PCOUT               => open,                   -- 48-bit output: Cascade output
    -- Control: 1-bit (each) output: Control Inputs/Status Bits
    OVERFLOW            => OVERFLOW_DSP4,             -- 1-bit output: Overflow in add/acc output
    PATTERNBDETECT      => PATTERNBDETECT_DSP4, -- 1-bit output: Pattern bar detect output
    PATTERNDETECT       => PATTERNDETECT_DSP4,   -- 1-bit output: Pattern detect output
    UNDERFLOW           => UNDERFLOW_DSP4,           -- 1-bit output: Underflow in add/acc output
    -- Data: 4-bit (each) output: Data Ports
    CARRYOUT            => open,             -- 4-bit output: Carry output
    P                   => P_DSP4,           -- 48-bit output: Primary data output
    -- Cascade: 30-bit (each) input: Cascade Ports
    ACIN                => ACIN_DSP4,                     -- 30-bit input: A cascade data input
    BCIN                => BCOUT_DSP3,                     -- 18-bit input: B cascade input
    CARRYCASCIN         => CARRYCASCIN_DSP4,       -- 1-bit input: Cascade carry input
    MULTSIGNIN          => MULTISIGNIN_DSP4,         -- 1-bit input: Multiplier sign input
    PCIN                => PCOUT_DSP3,                     -- 48-bit input: P cascade input
    -- Control: 4-bit (each) input: Control Inputs/Status Bits
    ALUMODE             => ALUMODE_DSP4,               -- 4-bit input: ALU control input
    CARRYINSEL          => CARRYINSEL_DSP4,         -- 3-bit input: Carry select input
    CLK                 => CLK,                       -- 1-bit input: Clock input
    INMODE              => INMODE_DSP4,                 -- 5-bit input: INMODE control input
    OPMODE              => OPMODE_DSP4,                 -- 7-bit input: Operation mode input
    -- Data: 30-bit (each) input: Data Ports
    A                   => A_DSP4,                -- 30-bit input: A data input
    B                   => B_DSP4,                -- 18-bit input: B data input
    C                   => C_DSP4,                           -- 48-bit input: C data input
    CARRYIN             => CARRYIN_DSP4,               -- 1-bit input: Carry input signal
    D                   => D_DSP4,                           -- 25-bit input: D data input
    -- Reset/Clock Enable: 1-bit (each) input: Reset/Clock Enable Inputs
    CEA1                => CE,                     -- 1-bit input: Clock enable input for 1st stage AREG
    CEA2                => CE,                     -- 1-bit input: Clock enable input for 2nd stage AREG
    CEAD                => CE,                     -- 1-bit input: Clock enable input for ADREG
    CEALUMODE           => CE,           -- 1-bit input: Clock enable input for ALUMODE
    CEB1                => CE,                     -- 1-bit input: Clock enable input for 1st stage BREG
    CEB2                => CE,                     -- 1-bit input: Clock enable input for 2nd stage BREG
    CEC                 => CE,                       -- 1-bit input: Clock enable input for CREG
    CECARRYIN           => CE,           -- 1-bit input: Clock enable input for CARRYINREG
    CECTRL              => CE,                 -- 1-bit input: Clock enable input for OPMODEREG and CARRYINSELREG
    CED                 => CE,                       -- 1-bit input: Clock enable input for DREG
    CEINMODE            => CE,             -- 1-bit input: Clock enable input for INMODEREG
    CEM                 => CE,                       -- 1-bit input: Clock enable input for MREG
    CEP                 => CE,                       -- 1-bit input: Clock enable input for PREG
    RSTA                => RST,                     -- 1-bit input: Reset input for AREG
    RSTALLCARRYIN       => RST,   -- 1-bit input: Reset input for CARRYINREG
    RSTALUMODE          => RST,         -- 1-bit input: Reset input for ALUMODEREG
    RSTB                => RST,                     -- 1-bit input: Reset input for BREG
    RSTC                => RST,                     -- 1-bit input: Reset input for CREG
    RSTCTRL             => RST,               -- 1-bit input: Reset input for OPMODEREG and CARRYINSELREG
    RSTD                => RST,                     -- 1-bit input: Reset input for DREG and ADREG
    RSTINMODE           => RST,           -- 1-bit input: Reset input for INMODEREG
    RSTM                => RST,                     -- 1-bit input: Reset input for MREG
    RSTP                => RST                      -- 1-bit input: Reset input for PREG
);

DSP48E1_inst_3 : DSP48E1
generic map (
    -- Feature Control Attributes: Data Path Selection
    A_INPUT             => "DIRECT",               -- Selects A input source, "DIRECT" (A port) or "CASCADE" (ACIN port)
    B_INPUT             => "DIRECT",               -- Selects B input source, "DIRECT" (B port) or "CASCADE" (BCIN port)
    USE_DPORT           => FALSE,                -- Select D port usage (TRUE or FALSE)
    USE_MULT            => "MULTIPLY",            -- Select multiplier usage ("MULTIPLY", "DYNAMIC", or "NONE")
    USE_SIMD            => "ONE48",               -- SIMD selection ("ONE48", "TWO24", "FOUR12")
    -- Pattern Detector Attributes: Pattern Detection Configuration
    AUTORESET_PATDET    => "NO_RESET",    -- "NO_RESET", "RESET_MATCH", "RESET_NOT_MATCH"
    MASK                => X"3fffffffffff",           -- 48-bit mask value for pattern detect (1=ignore)
    PATTERN             => X"000000000000",        -- 48-bit pattern match for pattern detect
    SEL_MASK            => "MASK",                -- "C", "MASK", "ROUNDING_MODE1", "ROUNDING_MODE2"
    SEL_PATTERN         => "PATTERN",          -- Select pattern value ("PATTERN" or "C")
    USE_PATTERN_DETECT  => "NO_PATDET",         -- Enable pattern detect ("PATDET" or "NO_PATDET")
    -- Register Control Attributes: Pipeline Register Configuration
    ACASCREG            => 1,                     -- Number of pipeline stages between A/ACIN and ACOUT (0, 1 or 2)
    ADREG               => 1,                        -- Number of pipeline stages for pre-adder (0 or 1)
    ALUMODEREG          => 1,                   -- Number of pipeline stages for ALUMODE (0 or 1)
    AREG                => 1,                         -- Number of pipeline stages for A (0, 1 or 2)
    BCASCREG            => 1,                     -- Number of pipeline stages between B/BCIN and BCOUT (0, 1 or 2)
    BREG                => 1,                         -- Number of pipeline stages for B (0, 1 or 2)
    CARRYINREG          => 1,                   -- Number of pipeline stages for CARRYIN (0 or 1)
    CARRYINSELREG       => 1,                -- Number of pipeline stages for CARRYINSEL (0 or 1)
    CREG                => 1,                         -- Number of pipeline stages for C (0 or 1)
    DREG                => 1,                         -- Number of pipeline stages for D (0 or 1)
    INMODEREG           => 1,                    -- Number of pipeline stages for INMODE (0 or 1)
    MREG                => 1,                         -- Number of multiplier pipeline stages (0 or 1)
    OPMODEREG           => 1,                    -- Number of pipeline stages for OPMODE (0 or 1)
    PREG                => 1                          -- Number of pipeline stages for P (0 or 1)
    )
port map (
    -- Cascade: 30-bit (each) output: Cascade Ports
    ACOUT               => ACOUT_DSP3,                   -- 30-bit output: A port cascade output
    BCOUT               => BCOUT_DSP3,                   -- 18-bit output: B port cascade output
    CARRYCASCOUT        => CARRYCASCOUT_DSP3,     -- 1-bit output: Cascade carry output
    MULTSIGNOUT         => MULTISIGNOUT_DSP3,       -- 1-bit output: Multiplier sign cascade output
    PCOUT               => PCOUT_DSP3,                   -- 48-bit output: Cascade output
    -- Control: 1-bit (each) output: Control Inputs/Status Bits
    OVERFLOW            => OVERFLOW_DSP3,             -- 1-bit output: Overflow in add/acc output
    PATTERNBDETECT      => PATTERNBDETECT_DSP3, -- 1-bit output: Pattern bar detect output
    PATTERNDETECT       => PATTERNDETECT_DSP3,   -- 1-bit output: Pattern detect output
    UNDERFLOW           => UNDERFLOW_DSP3,           -- 1-bit output: Underflow in add/acc output
    -- Data: 4-bit (each) output: Data Ports
    CARRYOUT            => open,             -- 4-bit output: Carry output
    P                   => P_DSP3,           -- 48-bit output: Primary data output
    -- Cascade: 30-bit (each) input: Cascade Ports
    ACIN                => ACIN_DSP3,                     -- 30-bit input: A cascade data input
    BCIN                => BCIN_DSP3,                     -- 18-bit input: B cascade input
    CARRYCASCIN         => CARRYCASCIN_DSP3,       -- 1-bit input: Cascade carry input
    MULTSIGNIN          => MULTISIGNIN_DSP3,         -- 1-bit input: Multiplier sign input
    PCIN                => PCOUT_DSP2,                     -- 48-bit input: P cascade input
    -- Control: 4-bit (each) input: Control Inputs/Status Bits
    ALUMODE             => ALUMODE_DSP3,               -- 4-bit input: ALU control input
    CARRYINSEL          => CARRYINSEL_DSP3,         -- 3-bit input: Carry select input
    CLK                 => CLK,                       -- 1-bit input: Clock input
    INMODE              => INMODE_DSP3,                 -- 5-bit input: INMODE control input
    OPMODE              => OPMODE_DSP3,                 -- 7-bit input: Operation mode input
    -- Data: 30-bit (each) input: Data Ports
    A                   => A_DSP3,                -- 30-bit input: A data input
    B                   => B_DSP3,                -- 18-bit input: B data input
    C                   => C_DSP3,                           -- 48-bit input: C data input
    CARRYIN             => CARRYIN_DSP3,               -- 1-bit input: Carry input signal
    D                   => D_DSP3,                           -- 25-bit input: D data input
    -- Reset/Clock Enable: 1-bit (each) input: Reset/Clock Enable Inputs
    CEA1                => CE,                     -- 1-bit input: Clock enable input for 1st stage AREG
    CEA2                => CE,                     -- 1-bit input: Clock enable input for 2nd stage AREG
    CEAD                => CE,                     -- 1-bit input: Clock enable input for ADREG
    CEALUMODE           => CE,           -- 1-bit input: Clock enable input for ALUMODE
    CEB1                => CE,                     -- 1-bit input: Clock enable input for 1st stage BREG
    CEB2                => CE,                     -- 1-bit input: Clock enable input for 2nd stage BREG
    CEC                 => CE,                       -- 1-bit input: Clock enable input for CREG
    CECARRYIN           => CE,           -- 1-bit input: Clock enable input for CARRYINREG
    CECTRL              => CE,                 -- 1-bit input: Clock enable input for OPMODEREG and CARRYINSELREG
    CED                 => CE,                       -- 1-bit input: Clock enable input for DREG
    CEINMODE            => CE,             -- 1-bit input: Clock enable input for INMODEREG
    CEM                 => CE,                       -- 1-bit input: Clock enable input for MREG
    CEP                 => CE,                       -- 1-bit input: Clock enable input for PREG
    RSTA                => RST,                     -- 1-bit input: Reset input for AREG
    RSTALLCARRYIN       => RST,   -- 1-bit input: Reset input for CARRYINREG
    RSTALUMODE          => RST,         -- 1-bit input: Reset input for ALUMODEREG
    RSTB                => RST,                     -- 1-bit input: Reset input for BREG
    RSTC                => RST,                     -- 1-bit input: Reset input for CREG
    RSTCTRL             => RST,               -- 1-bit input: Reset input for OPMODEREG and CARRYINSELREG
    RSTD                => RST,                     -- 1-bit input: Reset input for DREG and ADREG
    RSTINMODE           => RST,           -- 1-bit input: Reset input for INMODEREG
    RSTM                => RST,                     -- 1-bit input: Reset input for MREG
    RSTP                => RST                      -- 1-bit input: Reset input for PREG
);

DSP48E1_inst_2 : DSP48E1
generic map (
    -- Feature Control Attributes: Data Path Selection
    A_INPUT             => "DIRECT",               -- Selects A input source, "DIRECT" (A port) or "CASCADE" (ACIN port)
    B_INPUT             => "CASCADE",               -- Selects B input source, "DIRECT" (B port) or "CASCADE" (BCIN port)
    USE_DPORT           => FALSE,                -- Select D port usage (TRUE or FALSE)
    USE_MULT            => "MULTIPLY",            -- Select multiplier usage ("MULTIPLY", "DYNAMIC", or "NONE")
    USE_SIMD            => "ONE48",               -- SIMD selection ("ONE48", "TWO24", "FOUR12")
    -- Pattern Detector Attributes: Pattern Detection Configuration
    AUTORESET_PATDET    => "NO_RESET",    -- "NO_RESET", "RESET_MATCH", "RESET_NOT_MATCH"
    MASK                => X"3fffffffffff",           -- 48-bit mask value for pattern detect (1=ignore)
    PATTERN             => X"000000000000",        -- 48-bit pattern match for pattern detect
    SEL_MASK            => "MASK",                -- "C", "MASK", "ROUNDING_MODE1", "ROUNDING_MODE2"
    SEL_PATTERN         => "PATTERN",          -- Select pattern value ("PATTERN" or "C")
    USE_PATTERN_DETECT  => "NO_PATDET",         -- Enable pattern detect ("PATDET" or "NO_PATDET")
    -- Register Control Attributes: Pipeline Register Configuration
    ACASCREG            => 1,                     -- Number of pipeline stages between A/ACIN and ACOUT (0, 1 or 2)
    ADREG               => 1,                        -- Number of pipeline stages for pre-adder (0 or 1)
    ALUMODEREG          => 1,                   -- Number of pipeline stages for ALUMODE (0 or 1)
    AREG                => 1,                         -- Number of pipeline stages for A (0, 1 or 2)
    BCASCREG            => 1,                     -- Number of pipeline stages between B/BCIN and BCOUT (0, 1 or 2)
    BREG                => 1,                         -- Number of pipeline stages for B (0, 1 or 2)
    CARRYINREG          => 1,                   -- Number of pipeline stages for CARRYIN (0 or 1)
    CARRYINSELREG       => 1,                -- Number of pipeline stages for CARRYINSEL (0 or 1)
    CREG                => 1,                         -- Number of pipeline stages for C (0 or 1)
    DREG                => 1,                         -- Number of pipeline stages for D (0 or 1)
    INMODEREG           => 1,                    -- Number of pipeline stages for INMODE (0 or 1)
    MREG                => 1,                         -- Number of multiplier pipeline stages (0 or 1)
    OPMODEREG           => 1,                    -- Number of pipeline stages for OPMODE (0 or 1)
    PREG                => 1                          -- Number of pipeline stages for P (0 or 1)
    )
port map (
    -- Cascade: 30-bit (each) output: Cascade Ports
    ACOUT               => ACOUT_DSP2,                   -- 30-bit output: A port cascade output
    BCOUT               => BCOUT_DSP2,                   -- 18-bit output: B port cascade output
    CARRYCASCOUT        => CARRYCASCOUT_DSP2,     -- 1-bit output: Cascade carry output
    MULTSIGNOUT         => MULTISIGNOUT_DSP2,       -- 1-bit output: Multiplier sign cascade output
    PCOUT               => PCOUT_DSP2,                   -- 48-bit output: Cascade output
    -- Control: 1-bit (each) output: Control Inputs/Status Bits
    OVERFLOW            => OVERFLOW_DSP2,             -- 1-bit output: Overflow in add/acc output
    PATTERNBDETECT      => PATTERNBDETECT_DSP2, -- 1-bit output: Pattern bar detect output
    PATTERNDETECT       => PATTERNDETECT_DSP2,   -- 1-bit output: Pattern detect output
    UNDERFLOW           => UNDERFLOW_DSP2,           -- 1-bit output: Underflow in add/acc output
    -- Data: 4-bit (each) output: Data Ports
    CARRYOUT            => open,             -- 4-bit output: Carry output
    P                   => P_DSP2,           -- 48-bit output: Primary data output
    -- Cascade: 30-bit (each) input: Cascade Ports
    ACIN                => ACIN_DSP2,                     -- 30-bit input: A cascade data input
    BCIN                => BCOUT_DSP1,                     -- 18-bit input: B cascade input
    CARRYCASCIN         => CARRYCASCIN_DSP2,       -- 1-bit input: Cascade carry input
    MULTSIGNIN          => MULTISIGNIN_DSP2,         -- 1-bit input: Multiplier sign input
    PCIN                => PCOUT_DSP1,                     -- 48-bit input: P cascade input
    -- Control: 4-bit (each) input: Control Inputs/Status Bits
    ALUMODE             => ALUMODE_DSP2,               -- 4-bit input: ALU control input
    CARRYINSEL          => CARRYINSEL_DSP2,         -- 3-bit input: Carry select input
    CLK                 => CLK,                       -- 1-bit input: Clock input
    INMODE              => INMODE_DSP2,                 -- 5-bit input: INMODE control input
    OPMODE              => OPMODE_DSP2,                 -- 7-bit input: Operation mode input
    -- Data: 30-bit (each) input: Data Ports
    A                   => A_DSP2,                -- 30-bit input: A data input
    B                   => B_DSP2,                -- 18-bit input: B data input
    C                   => C_DSP2,                           -- 48-bit input: C data input
    CARRYIN             => CARRYIN_DSP2,               -- 1-bit input: Carry input signal
    D                   => D_DSP2,                           -- 25-bit input: D data input
    -- Reset/Clock Enable: 1-bit (each) input: Reset/Clock Enable Inputs
    CEA1                => CE,                     -- 1-bit input: Clock enable input for 1st stage AREG
    CEA2                => CE,                     -- 1-bit input: Clock enable input for 2nd stage AREG
    CEAD                => CE,                     -- 1-bit input: Clock enable input for ADREG
    CEALUMODE           => CE,           -- 1-bit input: Clock enable input for ALUMODE
    CEB1                => CE,                     -- 1-bit input: Clock enable input for 1st stage BREG
    CEB2                => CE,                     -- 1-bit input: Clock enable input for 2nd stage BREG
    CEC                 => CE,                       -- 1-bit input: Clock enable input for CREG
    CECARRYIN           => CE,           -- 1-bit input: Clock enable input for CARRYINREG
    CECTRL              => CE,                 -- 1-bit input: Clock enable input for OPMODEREG and CARRYINSELREG
    CED                 => CE,                       -- 1-bit input: Clock enable input for DREG
    CEINMODE            => CE,             -- 1-bit input: Clock enable input for INMODEREG
    CEM                 => CE,                       -- 1-bit input: Clock enable input for MREG
    CEP                 => CE,                       -- 1-bit input: Clock enable input for PREG
    RSTA                => RST,                     -- 1-bit input: Reset input for AREG
    RSTALLCARRYIN       => RST,   -- 1-bit input: Reset input for CARRYINREG
    RSTALUMODE          => RST,         -- 1-bit input: Reset input for ALUMODEREG
    RSTB                => RST,                     -- 1-bit input: Reset input for BREG
    RSTC                => RST,                     -- 1-bit input: Reset input for CREG
    RSTCTRL             => RST,               -- 1-bit input: Reset input for OPMODEREG and CARRYINSELREG
    RSTD                => RST,                     -- 1-bit input: Reset input for DREG and ADREG
    RSTINMODE           => RST,           -- 1-bit input: Reset input for INMODEREG
    RSTM                => RST,                     -- 1-bit input: Reset input for MREG
    RSTP                => RST                      -- 1-bit input: Reset input for PREG
);

DSP48E1_inst_1 : DSP48E1
generic map (
    -- Feature Control Attributes: Data Path Selection
    A_INPUT             => "DIRECT",               -- Selects A input source, "DIRECT" (A port) or "CASCADE" (ACIN port)
    B_INPUT             => "DIRECT",               -- Selects B input source, "DIRECT" (B port) or "CASCADE" (BCIN port)
    USE_DPORT           => FALSE,                -- Select D port usage (TRUE or FALSE)
    USE_MULT            => "MULTIPLY",            -- Select multiplier usage ("MULTIPLY", "DYNAMIC", or "NONE")
    USE_SIMD            => "ONE48",               -- SIMD selection ("ONE48", "TWO24", "FOUR12")
    -- Pattern Detector Attributes: Pattern Detection Configuration
    AUTORESET_PATDET    => "NO_RESET",    -- "NO_RESET", "RESET_MATCH", "RESET_NOT_MATCH"
    MASK                => X"3fffffffffff",           -- 48-bit mask value for pattern detect (1=ignore)
    PATTERN             => X"000000000000",        -- 48-bit pattern match for pattern detect
    SEL_MASK            => "MASK",                -- "C", "MASK", "ROUNDING_MODE1", "ROUNDING_MODE2"
    SEL_PATTERN         => "PATTERN",          -- Select pattern value ("PATTERN" or "C")
    USE_PATTERN_DETECT  => "NO_PATDET",         -- Enable pattern detect ("PATDET" or "NO_PATDET")
    -- Register Control Attributes: Pipeline Register Configuration
    ACASCREG            => 1,                     -- Number of pipeline stages between A/ACIN and ACOUT (0, 1 or 2)
    ADREG               => 1,                        -- Number of pipeline stages for pre-adder (0 or 1)
    ALUMODEREG          => 1,                   -- Number of pipeline stages for ALUMODE (0 or 1)
    AREG                => 1,                         -- Number of pipeline stages for A (0, 1 or 2)
    BCASCREG            => 1,                     -- Number of pipeline stages between B/BCIN and BCOUT (0, 1 or 2)
    BREG                => 1,                         -- Number of pipeline stages for B (0, 1 or 2)
    CARRYINREG          => 1,                   -- Number of pipeline stages for CARRYIN (0 or 1)
    CARRYINSELREG       => 1,                -- Number of pipeline stages for CARRYINSEL (0 or 1)
    CREG                => 1,                         -- Number of pipeline stages for C (0 or 1)
    DREG                => 1,                         -- Number of pipeline stages for D (0 or 1)
    INMODEREG           => 1,                    -- Number of pipeline stages for INMODE (0 or 1)
    MREG                => 1,                         -- Number of multiplier pipeline stages (0 or 1)
    OPMODEREG           => 1,                    -- Number of pipeline stages for OPMODE (0 or 1)
    PREG                => 1                          -- Number of pipeline stages for P (0 or 1)
    )
port map (
    -- Cascade: 30-bit (each) output: Cascade Ports
    ACOUT               => ACOUT_DSP1,                   -- 30-bit output: A port cascade output
    BCOUT               => BCOUT_DSP1,                   -- 18-bit output: B port cascade output
    CARRYCASCOUT        => CARRYCASCOUT_DSP1,     -- 1-bit output: Cascade carry output
    MULTSIGNOUT         => MULTISIGNOUT_DSP1,       -- 1-bit output: Multiplier sign cascade output
    PCOUT               => PCOUT_DSP1,                   -- 48-bit output: Cascade output
    -- Control: 1-bit (each) output: Control Inputs/Status Bits
    OVERFLOW            => OVERFLOW_DSP1,             -- 1-bit output: Overflow in add/acc output
    PATTERNBDETECT      => PATTERNBDETECT_DSP1, -- 1-bit output: Pattern bar detect output
    PATTERNDETECT       => PATTERNDETECT_DSP1,   -- 1-bit output: Pattern detect output
    UNDERFLOW           => UNDERFLOW_DSP1,           -- 1-bit output: Underflow in add/acc output
    -- Data: 4-bit (each) output: Data Ports
    CARRYOUT            => open,             -- 4-bit output: Carry output
    P                   => P_DSP1,           -- 48-bit output: Primary data output
    -- Cascade: 30-bit (each) input: Cascade Ports
    ACIN                => ACIN_DSP1,                     -- 30-bit input: A cascade data input
    BCIN                => BCIN_DSP1,                     -- 18-bit input: B cascade input
    CARRYCASCIN         => CARRYCASCIN_DSP1,       -- 1-bit input: Cascade carry input
    MULTSIGNIN          => MULTISIGNIN_DSP1,         -- 1-bit input: Multiplier sign input
    PCIN                => PCIN_DSP1,                     -- 48-bit input: P cascade input
    -- Control: 4-bit (each) input: Control Inputs/Status Bits
    ALUMODE             => ALUMODE_DSP1,               -- 4-bit input: ALU control input
    CARRYINSEL          => CARRYINSEL_DSP1,         -- 3-bit input: Carry select input
    CLK                 => CLK,                       -- 1-bit input: Clock input
    INMODE              => INMODE_DSP1,                 -- 5-bit input: INMODE control input
    OPMODE              => OPMODE_DSP1,                 -- 7-bit input: Operation mode input
    -- Data: 30-bit (each) input: Data Ports
    A                   => A_DSP1,                -- 30-bit input: A data input
    B                   => B_DSP1,                -- 18-bit input: B data input
    C                   => C_DSP1,                           -- 48-bit input: C data input
    CARRYIN             => CARRYIN_DSP1,               -- 1-bit input: Carry input signal
    D                   => D_DSP1,                           -- 25-bit input: D data input
    -- Reset/Clock Enable: 1-bit (each) input: Reset/Clock Enable Inputs
    CEA1                => CE,                     -- 1-bit input: Clock enable input for 1st stage AREG
    CEA2                => CE,                     -- 1-bit input: Clock enable input for 2nd stage AREG
    CEAD                => CE,                     -- 1-bit input: Clock enable input for ADREG
    CEALUMODE           => CE,           -- 1-bit input: Clock enable input for ALUMODE
    CEB1                => CE,                     -- 1-bit input: Clock enable input for 1st stage BREG
    CEB2                => CE,                     -- 1-bit input: Clock enable input for 2nd stage BREG
    CEC                 => CE,                       -- 1-bit input: Clock enable input for CREG
    CECARRYIN           => CE,           -- 1-bit input: Clock enable input for CARRYINREG
    CECTRL              => CE,                 -- 1-bit input: Clock enable input for OPMODEREG and CARRYINSELREG
    CED                 => CE,                       -- 1-bit input: Clock enable input for DREG
    CEINMODE            => CE,             -- 1-bit input: Clock enable input for INMODEREG
    CEM                 => CE,                       -- 1-bit input: Clock enable input for MREG
    CEP                 => CE,                       -- 1-bit input: Clock enable input for PREG
    RSTA                => RST,                     -- 1-bit input: Reset input for AREG
    RSTALLCARRYIN       => RST,   -- 1-bit input: Reset input for CARRYINREG
    RSTALUMODE          => RST,         -- 1-bit input: Reset input for ALUMODEREG
    RSTB                => RST,                     -- 1-bit input: Reset input for BREG
    RSTC                => RST,                     -- 1-bit input: Reset input for CREG
    RSTCTRL             => RST,               -- 1-bit input: Reset input for OPMODEREG and CARRYINSELREG
    RSTD                => RST,                     -- 1-bit input: Reset input for DREG and ADREG
    RSTINMODE           => RST,           -- 1-bit input: Reset input for INMODEREG
    RSTM                => RST,                     -- 1-bit input: Reset input for MREG
    RSTP                => RST                      -- 1-bit input: Reset input for PREG
);

-- ############################################################################

ALUMODE_DSP4 <= "0000";
ALUMODE_DSP3 <= "0000";
ALUMODE_DSP2 <= "0000";
ALUMODE_DSP1 <= "0000";

OPMODE_DSP4 <= "1010101";   -- (shift PCIN | M | M)
OPMODE_DSP3 <= "0010101";   -- (PCIN | M | M)
OPMODE_DSP2 <= "1010101";   -- (shift PCIN | M | M)
OPMODE_DSP1 <= "0000101";   -- (0 | M | M)


-- ############################################################################
--          DSP INPUT REGISTERS
-------------------------------------------------------------------------------

IRegA_Dsp4: component dsp_sreg_block
    generic map (
        WIDTH => 25,
        LENGTH => 3
    )
    port map (
        D => A_INPUT(41 downto 17),
        CLK => CLK,
        RST => RST,
        Q => A_DSP4(24 downto 0)
    );

IRegA_Dsp3: component dsp_sreg_block
    generic map (
        WIDTH => 18,
        LENGTH => 2
    )
    port map (
        D => A_DSP1(17 downto 0),
        CLK => CLK,
        RST => RST,
        Q => A_DSP3(17 downto 0)
    );

IRegB_Dsp3: component dsp_sreg_block
    generic map (
        WIDTH => 18,
        LENGTH => 2
    )
    port map (
        D => B_INPUT(34 downto 17),
        CLK => CLK,
        RST => RST,
        Q => B_DSP3(17 downto 0)
    );

IRegA_Dsp2: component dsp_dff_block
    generic map (
        WIDTH => 25
    )
    port map (
        D => A_INPUT(41 downto 17),
        CLK => CLK,
        RST => RST,
        Q => A_DSP2(24 downto 0)
    );

A_DSP1(17 downto 0) <= '0' & A_INPUT(16 downto 0);
B_DSP1(17 downto 0) <= '0' & B_INPUT(16 downto 0);

-------------------------------------------------------------------------------
--          DSP OUTPUT REGISTERS
-------------------------------------------------------------------------------

P_OUTPUT(75 downto 34) <= P_DSP4(41 downto 0);

ORegP_Dsp3: component dsp_dff_block
    generic map (
        WIDTH => 17
    )
    port map (
        D => P_DSP3(16 downto 0),
        CLK => CLK,
        RST => RST,
        Q => P_OUTPUT(33 downto 17)
    );

ORegP_Dsp1: component dsp_sreg_block
    generic map (
        WIDTH => 17,
        LENGTH => 3
    )
    port map (
        D => P_DSP1(16 downto 0),
        CLK => CLK,
        RST => RST,
        Q => P_OUTPUT(16 downto 0)
    );

-- ############################################################################

A_INPUT <= (41 downto 32 => '0') & LEFT;
B_INPUT <= (34 downto 32 => '0') & RIGHT;
MUL_OUT <= P_OUTPUT(31 downto 0);

end Behavioral;
