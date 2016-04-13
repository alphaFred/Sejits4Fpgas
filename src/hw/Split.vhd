library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;

use work.the_filter_package.all;


entity Split is
    Port (
        CLK             : in  std_logic;
        RST             : in  std_logic; -- low active
        VALID_IN        : in  std_logic; -- high active
        DATA_IN         : in  std_logic_vector(IN_BITWIDTH-1 downto 0);
        VALID_OUT       : out std_logic; -- high active
        DATA_OUT        : out std_logic_vector(OUT_BITWIDTH-1 downto 0)
        );
end Split;