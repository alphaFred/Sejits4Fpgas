----------------------------------------------------------------------------------
-- Company:
-- Engineer:
--
-- Create Date: 07/29/2015 12:03:12 PM
-- Design Name:
-- Module Name: dsp_sreg_block - Behavioral
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


entity DReg is
    Generic (
        WIDTH   : positive;
        LENGTH  : positive
    );
    Port (
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        VALID_IN : in STD_LOGIC;
        DREG_IN   : in STD_LOGIC_VECTOR (WIDTH-1 downto 0);
        VALID_OUT : out STD_LOGIC;
        DREG_OUT  : out STD_LOGIC_VECTOR (WIDTH-1 downto 0)
    );
end DReg;

architecture Behavioral of DReg is

    TYPE iBus is array(LENGTH-1 downto 0) of std_logic_vector(WIDTH-1 downto 0);
    TYPE iBus_VALID is array(LENGTH-1 downto 0) of std_logic;
    --
    signal sRegBus : iBus;
    signal ValidsRegBus : iBus_VALID;

    COMPONENT vector_dff_block
        Generic (
            WIDTH : positive
        );
        Port (
            D   : in STD_LOGIC_VECTOR (WIDTH-1 downto 0);
            CLK : in STD_LOGIC;
            RST : in STD_LOGIC;
            Q   : out STD_LOGIC_VECTOR (WIDTH-1 downto 0)
        );
    END COMPONENT;

    COMPONENT logic_dff_block
        Port (
            D   : in STD_LOGIC;
            CLK : in STD_LOGIC;
            RST : in STD_LOGIC;
            Q   : out STD_LOGIC
        );
    END COMPONENT;
begin
        shiftReg: for i in 1 to LENGTH generate
        begin
            dffLeft: if i = 1 generate
            begin
                dff: component vector_dff_block
                    generic map (
                        WIDTH => WIDTH
                    )
                    port map (
                        D => DREG_IN,
                        CLK => CLK,
                        RST => RST,
                        Q => sRegBus(i)
                    );
            end generate dffLeft;
            --
            dffOthers: if (i > 1 AND i < LENGTH) generate
            begin
                dff: component vector_dff_block
                    generic map (
                        WIDTH => WIDTH)
                    port map (
                        D => sRegBus(i-1),
                        CLK => CLK,
                        RST => RST,
                        Q => sRegBus(i)
                    );
            end generate dffOthers;
            --
            dffRight: if i = LENGTH generate
            begin
                dff: component vector_dff_block
                    generic map (
                        WIDTH => WIDTH)
                    port map (
                        D => sRegBus(i-1),
                        CLK => CLK,
                        RST => RST,
                        Q => DREG_OUT
                    );
            end generate dffRight;
        end generate shiftReg;

        validReg: for i in 1 to LENGTH generate
        begin
            validdffLeft: if i = 1 generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => VALID_IN,
                        CLK => CLK,
                        RST => RST,
                        Q => ValidsRegBus(i)
                    );
            end generate validdffLeft;
            --
            dffOthers: if (i > 1 AND i < LENGTH) generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => ValidsRegBus(i-1),
                        CLK => CLK,
                        RST => RST,
                        Q => ValidsRegBus(i)
                    );
            end generate dffOthers;
            --
            dffRight: if i = LENGTH generate
            begin
                valid_dff: component logic_dff_block
                    port map (
                        D => ValidsRegBus(i-1),
                        CLK => CLK,
                        RST => RST,
                        Q => VALID_OUT
                    );
            end generate dffRight;
        end generate validReg;
end architecture Behavioral;
