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

architecture BEHAVE of apply is                              signal BB_SUB_VALID_OUT_0 : std_logic;
    signal BB_SUB_OUT_0 : std_logic_vector(31 downto 0);                      begin                          
VhdlComponent : entity work.SubBB                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             LEFT => std_logic_vector(to_signed(255, 32)),
             RIGHT => a,
             VALID_OUT => BB_SUB_VALID_OUT_0,
             SUB_OUT => BB_SUB_OUT_0); 

-- RETURN
VALID_OUT <= BB_SUB_VALID_OUT_0;
MODULE_OUT <= BB_SUB_OUT_0;                      end BEHAVE;