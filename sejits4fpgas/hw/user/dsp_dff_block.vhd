----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 07/29/2015 11:33:59 AM
-- Design Name: 
-- Module Name: dsp_dff_block - Behavioral
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


entity dsp_dff_block is
    Generic (
        WIDTH : natural
    );
    Port (
        D : in STD_LOGIC_VECTOR (WIDTH-1 downto 0);
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        Q : out STD_LOGIC_VECTOR (WIDTH-1 downto 0)
    );
end dsp_dff_block;

architecture Behavioral of dsp_dff_block is
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
