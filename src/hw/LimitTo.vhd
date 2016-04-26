library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;


entity LimitTo is
    Generic(
        VALID_BITS      : positive
        );
    Port (
        CLK             : in  std_logic;
        RST             : in  std_logic; -- low active
        VALID_IN        : in  std_logic; -- high active
        DATA_IN         : in  std_logic_vector(31 downto 0);
        VALID_OUT       : out std_logic; -- high active
        DATA_OUT        : out std_logic_vector(31 downto 0)
        );
end LimitTo;

architecture limit_to_behave of LimitTo is
begin
    slice_full: if VALID_BITS >= 32 generate
    begin
        DATA_OUT <= DATA_IN;
    end generate slice_full;

    slice_limit: if VALID_BITS < 32 generate
    begin
        DATA_OUT <= (31 downto VALID_BITS => '0') & DATA_IN(VALID_BITS-1 downto 0);
    end generate slice_limit;

    VALID_OUT <= VALID_IN;
end limit_to_behave;
