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

architecture BEHAVE of apply is                              signal BB_SPLIT_VALID_OUT_0 : std_logic;
    signal n_3 : std_logic_vector(31 downto 0);
    signal BB_SPLIT_VALID_OUT_1 : std_logic;
    signal BB_SPLIT_OUT_0 : std_logic_vector(31 downto 0);
    signal BB_MERGE_VALID_OUT_0 : std_logic;
    signal BB_MERGE_OUT_0 : std_logic_vector(31 downto 0);
    signal BB_SPLIT_VALID_OUT_2 : std_logic;
    signal BB_SPLIT_OUT_1 : std_logic_vector(31 downto 0);
    signal BB_LIMITTO_VALID_OUT_0 : std_logic;
    signal BB_LIMITTO_OUT_0 : std_logic_vector(31 downto 0);                      begin                          
VhdlComponent : entity work.split                       
    generic map(INDEX => 3)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             DATA_IN => a,
             VALID_OUT => BB_SPLIT_VALID_OUT_0,
             DATA_OUT => n_3); 

VhdlComponent_1 : entity work.split                       
    generic map(INDEX => 2)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             DATA_IN => a,
             VALID_OUT => BB_SPLIT_VALID_OUT_1,
             DATA_OUT => BB_SPLIT_OUT_0); 

VhdlComponent_2 : entity work.merge                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => BB_SPLIT_VALID_OUT_0 AND BB_SPLIT_VALID_OUT_1,
             IN_3 => n_3,
             IN_2 => std_logic_vector(to_signed(255, 32)),
             IN_1 => std_logic_vector(to_signed(1, 32)),
             IN_0 => BB_SPLIT_OUT_0,
             VALID_OUT => BB_MERGE_VALID_OUT_0,
             DATA_OUT => BB_MERGE_OUT_0); 

VhdlComponent_3 : entity work.split                       
    generic map(INDEX => 1)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => BB_MERGE_VALID_OUT_0,
             DATA_IN => BB_MERGE_OUT_0,
             VALID_OUT => BB_SPLIT_VALID_OUT_2,
             DATA_OUT => BB_SPLIT_OUT_1); 

VhdlComponent_4 : entity work.limit_to                       
    generic map(VALID_BITS => 8)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => BB_SPLIT_VALID_OUT_2,
             DATA_IN => BB_SPLIT_OUT_1,
             VALID_OUT => BB_LIMITTO_VALID_OUT_0,
             DATA_OUT => BB_LIMITTO_OUT_0); 

-- RETURN
VALID_OUT <= BB_LIMITTO_VALID_OUT_0;
MODULE_OUT <= BB_LIMITTO_OUT_0;                      end BEHAVE;