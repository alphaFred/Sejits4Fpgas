library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;


entity vector_dff_block is
    Generic (
        WIDTH : positive := 8
    );
    Port (
        D : in STD_LOGIC_VECTOR (WIDTH-1 downto 0);
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        Q : out STD_LOGIC_VECTOR (WIDTH-1 downto 0)
    );
end vector_dff_block;

architecture Behavioral of vector_dff_block is
begin

process (RST, CLK)
begin
    if RST = '1' then
        Q <= (others => '0');
    elsif (CLK'event AND CLK = '1') then
        Q <= D;
    end if;
end process;
end Behavioral;