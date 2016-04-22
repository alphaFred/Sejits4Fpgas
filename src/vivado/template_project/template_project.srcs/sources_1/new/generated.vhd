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
         MODULE_OUT : out std_logic_vector(7 downto 0));                end apply;

architecture BEHAVE of apply is                              signal VhdlComponent_VALID_OUT_0 : std_logic;
    signal VhdlComponent_OUT_0 : std_logic_vector(31 downto 0);
    signal VhdlComponent_VALID_OUT_1 : std_logic;
    signal VhdlComponent_OUT_1 : std_logic_vector(7 downto 0);                      begin                          
VhdlComponent : entity work.SubBB                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             LEFT => a,
             RIGHT => std_logic_vector(to_signed(0, 32)),
             VALID_OUT => VhdlComponent_VALID_OUT_0,
             BINOP_OUT => VhdlComponent_OUT_0); 

VhdlComponent_1 : entity work.split                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VhdlComponent_VALID_OUT_0,
             DATA_IN => std_logic_vector(to_signed(255, 24)),
             INDEX => unsigned(VhdlComponent_OUT_0),
             VALID_OUT => VhdlComponent_VALID_OUT_1,
             DATA_OUT => VhdlComponent_OUT_1); 

-- RETURN
VALID_OUT <= VhdlComponent_VALID_OUT_1;
MODULE_OUT <= VhdlComponent_OUT_1;                      end BEHAVE;