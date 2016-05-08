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

architecture BEHAVE of apply is                              signal BB_CONVOLVE_VALID_OUT_0 : std_logic;
    signal d : std_logic_vector(31 downto 0);
    signal BB_ADD_VALID_OUT_0 : std_logic;
    signal c : std_logic_vector(31 downto 0);
    signal BB_SUB_VALID_OUT_0 : std_logic;
    signal BB_SUB_OUT_0 : std_logic_vector(31 downto 0);                      begin                          
VhdlComponent : entity work.Convolve                       
    generic map(FILTERMATRIX => (1, 2, 1, 2, 4, 2, 1, 2, 1),
                FILTER_SCALE => 16,
                IMG_WIDTH => 64,
                IMG_HEIGHT => 64)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             DATA_IN => a,
             VALID_OUT => BB_CONVOLVE_VALID_OUT_0,
             DATA_OUT => d); 

VhdlComponent_1 : entity work.AddBB                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             LEFT => a,
             RIGHT => std_logic_vector(to_signed(5, 32)),
             VALID_OUT => BB_ADD_VALID_OUT_0,
             ADD_OUT => c); 

VhdlComponent_2 : entity work.SubBB                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => BB_CONVOLVE_VALID_OUT_0 AND BB_ADD_VALID_OUT_0,
             LEFT => d,
             RIGHT => c,
             VALID_OUT => BB_SUB_VALID_OUT_0,
             SUB_OUT => BB_SUB_OUT_0); 

-- RETURN
VALID_OUT <= BB_SUB_VALID_OUT_0;
MODULE_OUT <= BB_SUB_OUT_0;                      end BEHAVE;