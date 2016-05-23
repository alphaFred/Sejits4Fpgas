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
        WIDTH   : positive :=32;
        LENGTH  : positive :=4
    );
    Port (
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        VALID_IN : in STD_LOGIC;
        READY_IN : in std_logic;
        DREG_IN   : in STD_LOGIC_VECTOR (WIDTH-1 downto 0);
        VALID_OUT : out STD_LOGIC;
        READY_OUT : out std_logic;
        DREG_OUT  : out STD_LOGIC_VECTOR (WIDTH-1 downto 0)
    );
end DReg;

architecture Behavioral of DReg is

    TYPE iBus is array(LENGTH-1 downto 0) of std_logic_vector(WIDTH-1 downto 0);
    TYPE iBus_VALID is array(LENGTH-1 downto 0) of std_logic;
    --
    signal sRegBus : iBus;
    signal ValidsRegBus : iBus_VALID := (others => '0');

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

    constant depth_select_bits : positive := 2; -- specify depth

    signal srl_select : std_logic_vector(LENGTH-1 downto 0); -- Dynamic select input to SRL
    signal srl_out : std_logic_vector(WIDTH-1 downto 0); -- intermediate signal between srl and register

    type array_slv is array (WIDTH-1 downto 0) of std_logic_vector(LENGTH-1 downto 0);
    signal shift_reg : array_slv;
begin
    -- Add the below after begin keyword in architecture
    process (CLK)
    begin
       if CLK'event and CLK='1' then
           for i in 0 to WIDTH-1 loop
               shift_reg(i) <= shift_reg(i)(LENGTH-2 downto 0) & DREG_IN(i);
           end loop;
       end if;
    end process;

    process(shift_reg,srl_select)
    begin
       for i in 0 to WIDTH-1 loop
          srl_out(i) <= shift_reg(i)(LENGTH-3);
       end loop;
    end process;

    process(CLK)
    begin
      if CLK'event and CLK='1' then
           DREG_OUT <= srl_out;
      end if;
    end process;
    
        validReg: for i in 1 to LENGTH-1 generate
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
            dffRight: if i = LENGTH-1 generate
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

    READY_OUT <= READY_IN;
end architecture Behavioral;
