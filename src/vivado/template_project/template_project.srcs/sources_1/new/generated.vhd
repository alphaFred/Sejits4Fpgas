library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.the_filter_package.all;


entity apply is                    
    port(CLK : in std_logic;
         RST : in std_logic;
         VALID_IN : in std_logic;
         a : in std_logic_vector(31 downto 0);
         VALID_OUT : out std_logic;
         MODULE_OUT : out std_logic_vector(31 downto 0));                end apply;

architecture BEHAVE of apply is                              signal BB_MERGE_VALID_OUT_0 : std_logic;
    signal n_1 : std_logic_vector(31 downto 0);
    signal BB_SPLIT_VALID_OUT_0 : std_logic;
    signal BB_SPLIT_OUT_0 : std_logic_vector(31 downto 0);
    signal BB_SPLIT_VALID_OUT_1 : std_logic;
    signal BB_SPLIT_OUT_1 : std_logic_vector(31 downto 0);                      begin                          
VhdlComponent : entity work.merge                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             IN_3 => std_logic_vector(to_signed(0, 32)),
             IN_2 => a,
             VALID_OUT => BB_MERGE_VALID_OUT_0,
             DATA_OUT => n_1); 

VhdlComponent_1 : entity work.split                       
    generic map(INDEX => 2)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             DATA_IN => a,
             VALID_OUT => BB_SPLIT_VALID_OUT_0,
             DATA_OUT => BB_SPLIT_OUT_0); 

VhdlComponent_2 : entity work.split                       
    generic map(INDEX => 0)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => BB_MERGE_VALID_OUT_0 AND BB_SPLIT_VALID_OUT_0,
             DATA_IN => std_logic_vector(to_signed(255, 32)),
             VALID_OUT => BB_SPLIT_VALID_OUT_1,
             DATA_OUT => BB_SPLIT_OUT_1); 

-- RETURN
VALID_OUT <= BB_SPLIT_VALID_OUT_1;
MODULE_OUT <= BB_SPLIT_OUT_1;                      end BEHAVE;