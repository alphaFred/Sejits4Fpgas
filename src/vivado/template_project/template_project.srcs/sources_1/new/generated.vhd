library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.the_filter_package.all;


entity apply is                    
    port(CLK : in std_logic;
         RST : in std_logic;
         VALID_IN : in std_logic;
         READY_IN : in std_logic;
         a : in std_logic_vector(31 downto 0);
         VALID_OUT : out std_logic;
         READY_OUT : out std_logic;
         MODULE_OUT : out std_logic_vector(31 downto 0));                end apply;

architecture BEHAVE of apply is                              signal BB_ADD_READY_OUT_0 : std_logic;
    signal BB_ADD_VALID_OUT_0 : std_logic;
    signal BB_ADD_OUT_0 : std_logic_vector(31 downto 0);                      begin                          
VhdlComponent : entity work.AddBB                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             READY_IN => READY_IN,
             LEFT => a,
             RIGHT => std_logic_vector(to_signed(10, 32)),
             READY_OUT => BB_ADD_READY_OUT_0,
             VALID_OUT => BB_ADD_VALID_OUT_0,
             ADD_OUT => BB_ADD_OUT_0); 

-- RETURN
VALID_OUT <= BB_ADD_VALID_OUT_0;
READY_OUT <= BB_ADD_READY_OUT_0;
MODULE_OUT <= BB_ADD_OUT_0;                      end BEHAVE;