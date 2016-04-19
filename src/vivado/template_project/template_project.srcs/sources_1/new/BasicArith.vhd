library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNIMACRO;
use UNIMACRO.vcomponents.all;

Library UNISIM;
use UNISIM.vcomponents.all;


ENTITY BasicArith IS
    GENERIC (
        OP      : integer
        );
    PORT (
        CLK         : in STD_LOGIC;
        RST         : in STD_LOGIC;
        VALID_IN    : in STD_LOGIC;
        LEFT        : in STD_LOGIC_VECTOR(7 downto 0);
        RIGHT       : in STD_LOGIC_VECTOR(7 downto 0);
        VALID_OUT   : out STD_LOGIC;
        BINOP_OUT  : out STD_LOGIC_VECTOR(7 downto 0)
        );
END BasicArith;

ARCHITECTURE BasicArith_Behave OF BasicArith IS
    -- BEGIN    DSP48E1_inst_1
    signal MULTISIGNOUT_DSP1 : std_logic;
    signal CARRYCASCOUT_DSP1 : std_logic;
    --
    signal OVERFLOW_DSP1 : std_logic;
    signal PATTERNBDETECT_DSP1 : std_logic;
    signal PATTERNDETECT_DSP1 : std_logic;
    signal UNDERFLOW_DSP1 : std_logic;
    --
    signal P_DSP1 : std_logic_vector(47 downto 0);
    --
    signal ACIN_DSP1 : std_logic_vector(29 downto 0) := (others => '0');
    signal BCIN_DSP1 : std_logic_vector(17 downto 0) := (others => '0');
    --
    signal ACOUT_DSP1 : std_logic_vector(29 downto 0);
    signal BCOUT_DSP1 : std_logic_vector(17 downto 0);
    --
    signal CARRYCASCIN_DSP1 : std_logic := '0';
    signal MULTISIGNIN_DSP1 : std_logic := '0';
    signal PCIN_DSP1 : std_logic_vector(47 downto 0) := (others => '0');
    signal PCOUT_DSP1 : std_logic_vector(47 downto 0);
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
    constant DELAY_ADD_SUB : positive := 3;
    constant DELAY_MUL     : positive := 4;
    --
    TYPE iBus_ADD_SUB is array(DELAY_ADD_SUB-1 downto 0) of std_logic;
    TYPE iBus_MUL is array(DELAY_MUL-1 downto 0) of std_logic;
    --
    signal ValidsRegBus_ADD_SUB : iBus_ADD_SUB := (others => '0');
    signal ValidsRegBus_MUL     : iBus_MUL := (others => '0');
    --
    signal nRST : std_logic;
    --
    COMPONENT logic_dff_block
    Port (
        D   : in STD_LOGIC;
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        Q   : out STD_LOGIC
    );
    END COMPONENT;
BEGIN
    nRST <= not RST;
    --
    DSP48E1_inst_1 : DSP48E1
    generic map (
        A_INPUT             => "DIRECT",
        B_INPUT             => "DIRECT",
        USE_DPORT           => FALSE,
        USE_MULT            => "MULTIPLY",
        USE_SIMD            => "ONE48",
        AUTORESET_PATDET    => "NO_RESET",
        MASK                => X"0000000000ff",
        PATTERN             => X"000000000000",
        SEL_MASK            => "MASK",
        SEL_PATTERN         => "PATTERN",
        USE_PATTERN_DETECT  => "PATDET",
        ACASCREG            => 1,
        ADREG               => 1,
        ALUMODEREG          => 1,
        AREG                => 1,
        BCASCREG            => 1,
        BREG                => 1,
        CARRYINREG          => 1,
        CARRYINSELREG       => 1,
        CREG                => 1,
        DREG                => 1,
        INMODEREG           => 1,
        MREG                => 1,
        OPMODEREG           => 1,
        PREG                => 1
        )
    port map (
        -- Cascade: 30-bit (each) output: Cascade Ports
        ACOUT               => ACOUT_DSP1,
        BCOUT               => BCOUT_DSP1,
        CARRYCASCOUT        => CARRYCASCOUT_DSP1,
        MULTSIGNOUT         => MULTISIGNOUT_DSP1,
        PCOUT               => PCOUT_DSP1,
        -- Control: 1-bit (each) output: Control Inputs/Status Bits
        OVERFLOW            => OVERFLOW_DSP1,
        PATTERNBDETECT      => PATTERNBDETECT_DSP1,
        PATTERNDETECT       => PATTERNDETECT_DSP1,
        UNDERFLOW           => UNDERFLOW_DSP1,
        -- Data: 4-bit (each) output: Data Ports
        CARRYOUT            => open,
        P                   => P_DSP1,
        -- Cascade: 30-bit (each) input: Cascade Ports
        ACIN                => ACIN_DSP1,
        BCIN                => BCIN_DSP1,
        CARRYCASCIN         => CARRYCASCIN_DSP1,
        MULTSIGNIN          => MULTISIGNIN_DSP1,
        PCIN                => PCIN_DSP1,
        -- Control: 4-bit (each) input: Control Inputs/Status Bits
        ALUMODE             => ALUMODE_DSP1,
        CARRYINSEL          => CARRYINSEL_DSP1,
        CLK                 => CLK,
        INMODE              => INMODE_DSP1,
        OPMODE              => OPMODE_DSP1,
        -- Data: 30-bit (each) input: Data Ports
        A                   => A_DSP1,
        B                   => B_DSP1,
        C                   => C_DSP1,
        CARRYIN             => CARRYIN_DSP1,
        D                   => D_DSP1,
        -- Reset/Clock Enable: 1-bit (each) input: Reset/Clock Enable Inputs
        CEA1                => '1',
        CEA2                => '1',
        CEAD                => '1',
        CEALUMODE           => '1',
        CEB1                => '1',
        CEB2                => '1',
        CEC                 => '1',
        CECARRYIN           => '1',
        CECTRL              => '1',
        CED                 => '1',
        CEINMODE            => '1',
        CEM                 => '1',
        CEP                 => '1',
        RSTA                => nRST,
        RSTALLCARRYIN       => nRST,
        RSTALUMODE          => nRST,
        RSTB                => nRST,
        RSTC                => nRST,
        RSTCTRL             => nRST,
        RSTD                => nRST,
        RSTINMODE           => nRST,
        RSTM                => nRST,
        RSTP                => nRST
    );

    validReg_ADD: if OP = 0 generate
    begin
        validReg_ADD_int: for i in 0 to DELAY_ADD_SUB generate
        begin
            validdffLeft_ADD: if i = 0 generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => VALID_IN,
                        CLK => CLK,
                        RST => nRST,
                        Q => ValidsRegBus_ADD_SUB(i)
                    );
            end generate validdffLeft_ADD;
            --
            dffOthers_ADD: if (i > 0 AND i < DELAY_ADD_SUB) generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => ValidsRegBus_ADD_SUB(i-1),
                        CLK => CLK,
                        RST => not RST,
                        Q => ValidsRegBus_ADD_SUB(i)
                    );
            end generate dffOthers_ADD;
            --
            dffRight_ADD: if i = DELAY_ADD_SUB generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => ValidsRegBus_ADD_SUB(i-1),
                        CLK => CLK,
                        RST => nRST,
                        Q => VALID_OUT
                    );
            end generate dffRight_ADD;
        end generate validReg_ADD_int;
    end generate validReg_ADD;

    validReg_SUB: if OP = 1 generate
    begin
        validReg_SUB_int: for i in 0 to DELAY_ADD_SUB generate
        begin
            validdffLeft_SUB: if i = 0 generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => VALID_IN,
                        CLK => CLK,
                        RST => nRST,
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
                        RST => nRST,
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
                        RST => nRST,
                        Q => VALID_OUT
                    );
            end generate dffRight_SUB;
        end generate validReg_SUB_int;
    end generate validReg_SUB;

    validReg_MUL: if OP = 2 generate
    begin
        validReg_MUL_int: for i in 0 to DELAY_MUL generate
        begin
            validdffLeft_MUL: if i = 0 generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => VALID_IN,
                        CLK => CLK,
                        RST => nRST,
                        Q => ValidsRegBus_MUL(i)
                    );
            end generate validdffLeft_MUL;
            --
            dffOthers_MUL: if (i > 0 AND i < DELAY_MUL) generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => ValidsRegBus_MUL(i-1),
                        CLK => CLK,
                        RST => nRST,
                        Q => ValidsRegBus_MUL(i)
                    );
            end generate dffOthers_MUL;
            --
            dffRight_MUL: if i = DELAY_MUL generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => ValidsRegBus_MUL(i-1),
                        CLK => CLK,
                        RST => nRST,
                        Q => VALID_OUT
                    );
            end generate dffRight_MUL;
        end generate validReg_MUL_int;
    end generate validReg_MUL;


    OP0:IF OP = 0 GENERATE
    -- OP = 0 => Add
        INMODE_DSP1 <= "00000";
        OPMODE_DSP1 <= "0110011";   -- (Z=C | Y=0 | X=A:B)
        ALUMODE_DSP1 <= "0000";     --  Z + X + Y + CIN
    END GENERATE;

    OP1:IF OP = 1 GENERATE
    -- OP = 1 => Substract
        INMODE_DSP1 <= "00000";
        OPMODE_DSP1 <= "0110011";   -- (Z=C | Y=0 | X=A:B)
        ALUMODE_DSP1 <= "0011";     --  Z ??? (X + Y + CIN)
    END GENERATE;

    OP2:IF OP = 2 GENERATE
        -- OP = 2 => Multiply
        INMODE_DSP1 <= "10001";     -- Multiplyer Inport: B1 | A1
        OPMODE_DSP1 <= "0000101";   -- (Z=0 | Y=M | X=M)
        ALUMODE_DSP1 <= "0000";     --  Z + X + Y + CIN
    END GENERATE;

    run : PROCESS (CLK)
    BEGIN
        IF CLK'EVENT AND CLK = '1' THEN
            IF OP = 0 THEN
                A_DSP1 <= (29 downto 0 => '0');
                -- Pack RIGHT input into A:B
                B_DSP1 <= (17 downto 8 => '0') & RIGHT;
                -- B_DSP1 <= (17 downto 8 => '0') & RIGHT;
                -- Pack LEFT input into C
                C_DSP1 <= (47 downto 8 => '0') & LEFT;
            ELSIF OP = 1 THEN
                A_DSP1 <= (29 downto 0 => '0');
                -- Pack RIGHT input into A:B
                B_DSP1 <= (17 downto 8 => '0') & RIGHT;
                -- Pack LEFT input into C
                C_DSP1 <= (47 downto 8 => '0') & LEFT;
            ELSIF OP = 2 THEN
                C_DSP1 <= (47 downto 0 => '0');
                -- Pack RIGHT input into A:B
                A_DSP1 <= (29 downto 8 => '0') & LEFT;
                B_DSP1 <= (17 downto 8 => '0') & RIGHT;
            ELSE
                A_DSP1 <= (29 downto 0 => '0');
                -- Pack RIGHT input into A:B
                B_DSP1 <= (17 downto 8 => '0') & RIGHT;
                -- Pack LEFT input into C
                C_DSP1 <= (47 downto 8 => '0') & LEFT;
            END IF;
            --
            IF signed(P_DSP1) > 255 THEN
                BINOP_OUT <= (others => '1');
            ELSIF signed(P_DSP1) < 0 THEN
                BINOP_OUT <= (others => '0');
            ELSE
                BINOP_OUT <= P_DSP1(7 downto 0);
            END IF;
        END IF;
    END PROCESS;
END BasicArith_Behave;
