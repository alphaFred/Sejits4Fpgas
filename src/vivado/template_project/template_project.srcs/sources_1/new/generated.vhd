library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.the_filter_package.all;


entity apply is                    
    port(CLK : in std_logic;
         RST : in std_logic;
         VALID_IN : in std_logic;
         READY_IN : in std_logic;
         img : in std_logic_vector(31 downto 0);
         VALID_OUT : out std_logic;
         READY_OUT : out std_logic;
         MODULE_OUT : out std_logic_vector(31 downto 0));                end apply;

architecture BEHAVE of apply is                              signal VhdlDReg_READY_OUT_1 : std_logic;
    signal VhdlDReg_VALID_OUT_1 : std_logic;
    signal img_DREG_1 : std_logic_vector(31 downto 0);
    signal VhdlDReg_READY_OUT_0 : std_logic;
    signal VhdlDReg_VALID_OUT_0 : std_logic;
    signal img_DREG_0 : std_logic_vector(31 downto 0);
    signal BB_CONVOLVE_READY_OUT_0 : std_logic;
    signal BB_CONVOLVE_VALID_OUT_0 : std_logic;
    signal a : std_logic_vector(31 downto 0);
    signal BB_SUB_READY_OUT_0 : std_logic;
    signal BB_SUB_VALID_OUT_0 : std_logic;
    signal b : std_logic_vector(31 downto 0);
    signal BB_CONVOLVE_READY_OUT_1 : std_logic;
    signal BB_CONVOLVE_VALID_OUT_1 : std_logic;
    signal c : std_logic_vector(31 downto 0);
    signal BB_ADD_READY_OUT_0 : std_logic;
    signal BB_ADD_VALID_OUT_0 : std_logic;
    signal BB_ADD_OUT_0 : std_logic_vector(31 downto 0);                      begin                          

VhdlDReg : entity work.DReg                       
    generic map(WIDTH => 32,
                LENGTH => 2592)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             READY_IN => READY_IN,
             DREG_IN => img,
             READY_OUT => VhdlDReg_READY_OUT_1,
             VALID_OUT => VhdlDReg_VALID_OUT_1,
             DREG_OUT => img_DREG_1); 


VhdlDReg_1 : entity work.DReg                       
    generic map(WIDTH => 32,
                LENGTH => 1291)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             READY_IN => READY_IN,
             DREG_IN => img,
             READY_OUT => VhdlDReg_READY_OUT_0,
             VALID_OUT => VhdlDReg_VALID_OUT_0,
             DREG_OUT => img_DREG_0); 

VhdlComponent : entity work.Convolve                       
    generic map(FILTERMATRIX => (-1, 0, 1, -2, 0, 2, -1, 0, 1),
                FILTER_SCALE => 16,
                IMG_WIDTH => 640,
                IMG_HEIGHT => 480)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             READY_IN => READY_IN,
             DATA_IN => img,
             READY_OUT => BB_CONVOLVE_READY_OUT_0,
             VALID_OUT => BB_CONVOLVE_VALID_OUT_0,
             DATA_OUT => a); 

VhdlComponent_1 : entity work.SubBB                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VhdlDReg_VALID_OUT_0 AND BB_CONVOLVE_VALID_OUT_0,
             READY_IN => VhdlDReg_READY_OUT_0 AND BB_CONVOLVE_READY_OUT_0,
             LEFT => img_DREG_0,
             RIGHT => a,
             READY_OUT => BB_SUB_READY_OUT_0,
             VALID_OUT => BB_SUB_VALID_OUT_0,
             SUB_OUT => b); 

VhdlComponent_2 : entity work.Convolve                       
    generic map(FILTERMATRIX => (1, 2, 1, 2, 4, 2, 1, 2, 1),
                FILTER_SCALE => 16,
                IMG_WIDTH => 640,
                IMG_HEIGHT => 480)                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => BB_SUB_VALID_OUT_0,
             READY_IN => BB_SUB_READY_OUT_0,
             DATA_IN => b,
             READY_OUT => BB_CONVOLVE_READY_OUT_1,
             VALID_OUT => BB_CONVOLVE_VALID_OUT_1,
             DATA_OUT => c); 

VhdlComponent_3 : entity work.AddBB                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VhdlDReg_VALID_OUT_1 AND BB_CONVOLVE_VALID_OUT_1,
             READY_IN => VhdlDReg_READY_OUT_1 AND BB_CONVOLVE_READY_OUT_1,
             LEFT => img_DREG_1,
             RIGHT => c,
             READY_OUT => BB_ADD_READY_OUT_0,
             VALID_OUT => BB_ADD_VALID_OUT_0,
             ADD_OUT => BB_ADD_OUT_0); 

-- RETURN
VALID_OUT <= BB_ADD_VALID_OUT_0;
READY_OUT <= BB_ADD_READY_OUT_0;
MODULE_OUT <= BB_ADD_OUT_0;                      end BEHAVE;