library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.the_filter_package.all;


entity apply is                    
    port(CLK : in std_logic;
         RST : in std_logic;
         VALID_IN : in std_logic;
         a : in std_logic_vector(7 downto 0);
         VALID_OUT : out std_logic;
         MODULE_OUT : out std_logic_vector(7 downto 0));                end apply;

architecture BEHAVE of apply is                              signal VhdlBinaryOp_VALID_OUT_0 : std_logic;
    signal c : std_logic_vector(7 downto 0);
    signal VhdlComponent_VALID_OUT_1 : std_logic;
    signal VhdlComponent_OUT_0 : std_logic_vector(7 downto 0);                      begin                          
VhdlBinaryOp : entity work.BasicArith                       
    generic map(OP => 1)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             LEFT => std_logic_vector(to_signed(255, 8)),
             RIGHT => a,
             VALID_OUT => VhdlBinaryOp_VALID_OUT_0,
             BINOP_OUT => c); 

VhdlComponent : entity work.Convolve                       
    generic map(FILTERMATRIX => (1, 2, 1, 2, 4, 2, 1, 2, 1),
                FILTER_SCALE => 16,
                IMG_WIDTH => 640,
                IMG_HEIGHT => 480,
                IN_BITWIDTH => 8,
                OUT_BITWIDTH => 8)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VhdlBinaryOp_VALID_OUT_0,
             DATA_IN => c,
             VALID_OUT => VhdlComponent_VALID_OUT_1,
             DATA_OUT => VhdlComponent_OUT_0); 

-- RETURN
VALID_OUT <= VhdlComponent_VALID_OUT_1;
MODULE_OUT <= VhdlComponent_OUT_0;                      end BEHAVE;