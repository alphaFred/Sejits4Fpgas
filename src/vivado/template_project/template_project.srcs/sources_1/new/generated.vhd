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
    signal VhdlBinaryOp_OUT_0 : std_logic_vector(7 downto 0);                      begin                          
VhdlBinaryOp : entity work.BasicArith                       
    generic map(OP => 1)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             LEFT => std_logic_vector(to_signed(255, 8)),
             RIGHT => a,
             VALID_OUT => VhdlBinaryOp_VALID_OUT_0,
             BINOP_OUT => VhdlBinaryOp_OUT_0); 

-- RETURN
VALID_OUT <= VhdlBinaryOp_VALID_OUT_0;
MODULE_OUT <= VhdlBinaryOp_OUT_0;                      end BEHAVE;