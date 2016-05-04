library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;


entity Split is
    Generic (
        INDEX           : integer
        );
    Port (
        CLK             : in  std_logic;
        RST             : in  std_logic; -- low active
        VALID_IN        : in  std_logic; -- high active
        DATA_IN         : in  std_logic_vector(31 downto 0);
        VALID_OUT       : out std_logic; -- high active
        DATA_OUT        : out std_logic_vector(31 downto 0)
        );
end Split;

architecture split_behave of Split is
begin
    slice_0: if INDEX = 0 generate
    begin
        DATA_OUT <= (31 downto 8 => '0') & DATA_IN(7 downto 0);
    end generate slice_0;

    slice_1: if INDEX = 1 generate
    begin
        DATA_OUT <= (31 downto 16 => '0') & DATA_IN(15 downto 8) & (7 downto 0 => '0');
    end generate slice_1;

    slice_2: if INDEX = 2 generate
    begin
        DATA_OUT <= (31 downto 24 => '0') & DATA_IN(23 downto 16) & (15 downto 0 => '0');
    end generate slice_2;

    slice_3: if INDEX = 3 generate
    begin
        DATA_OUT <= DATA_IN(31 downto 24) & (23 downto 0 => '0');
    end generate slice_3;

    VALID_OUT <= VALID_IN;
end split_behave;
