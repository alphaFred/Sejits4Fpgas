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

architecture BEHAVE of apply is                              signal VhdlComponent_VALID_OUT_0 : std_logic;
    signal VhdlComponent_OUT_0 : std_logic_vector(31 downto 0);
    signal VhdlComponent_VALID_OUT_1 : std_logic;
    signal VhdlComponent_OUT_1 : std_logic_vector(31 downto 0);
    signal VhdlComponent_VALID_OUT_2 : std_logic;
    signal VhdlComponent_OUT_2 : std_logic_vector(31 downto 0);                      begin                          
VhdlComponent : entity work.split                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             DATA_IN => a,
             INDEX => to_unsigned(0, 8),
             VALID_OUT => VhdlComponent_VALID_OUT_0,
             DATA_OUT => VhdlComponent_OUT_0); 

VhdlComponent_1 : entity work.Convolve                       
    generic map(FILTERMATRIX => (-1, 0, 1, -2, 0, 2, -1, 0, 1),
                FILTER_SCALE => 16,
                IMG_WIDTH => 315,
                IMG_HEIGHT => 300)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VhdlComponent_VALID_OUT_0,
             DATA_IN => VhdlComponent_OUT_0,
             VALID_OUT => VhdlComponent_VALID_OUT_1,
             DATA_OUT => VhdlComponent_OUT_1); 

VhdlComponent_2 : entity work.Convolve                       
    generic map(FILTERMATRIX => (1, 2, 1, 2, 4, 2, 1, 2, 1),
                FILTER_SCALE => 16,
                IMG_WIDTH => 315,
                IMG_HEIGHT => 300)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VhdlComponent_VALID_OUT_1,
             DATA_IN => VhdlComponent_OUT_1,
             VALID_OUT => VhdlComponent_VALID_OUT_2,
             DATA_OUT => VhdlComponent_OUT_2); 

-- RETURN
VALID_OUT <= VhdlComponent_VALID_OUT_2;
MODULE_OUT <= VhdlComponent_OUT_2;                      end BEHAVE;