library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;


entity Merge is
    Port (
        CLK             : in  std_logic;
        RST             : in  std_logic; -- low active
        VALID_IN        : in  std_logic; -- high active
        READY_IN        : in  std_logic;
        IN_3            : in  std_logic_vector(31 downto 0);
        IN_2            : in  std_logic_vector(31 downto 0);
        IN_1            : in  std_logic_vector(31 downto 0);
        IN_0            : in  std_logic_vector(31 downto 0);
        VALID_OUT       : out std_logic; -- high active
        READY_OUT       : out std_logic;
        DATA_OUT        : out std_logic_vector(31 downto 0)
        );
end Merge;

architecture merge_behave of Merge is
begin
    DATA_OUT <= IN_3(7 downto 0) & IN_2(7 downto 0) & IN_1(7 downto 0) & IN_0(7 downto 0);
    VALID_OUT <= VALID_IN;
    READY_OUT <= READY_IN;
end merge_behave;
