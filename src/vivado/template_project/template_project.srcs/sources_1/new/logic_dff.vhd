library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;


entity logic_dff_block is
    Port (
        D : in STD_LOGIC;
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        Q : out STD_LOGIC
    );
end logic_dff_block;

architecture Behavioral of logic_dff_block is
begin

process (RST, CLK)
begin
    if RST = '1' then
        Q <= '0';
    elsif (CLK'event AND CLK = '1') then
        Q <= D;
    end if;
end process;

end Behavioral;