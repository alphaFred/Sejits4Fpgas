library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use work.the_filter_package.all;


entity accel_wrapper is                    
    port(CLK : in std_logic;
         RST : in std_logic;
         VALID_IN : in std_logic;
         m_axis_mm2s_tdata : in std_logic_vector(31 downto 0);
         m_axis_mm2s_tlast : in std_logic;
         s_axis_s2mm_tready : in std_logic;
         VALID_OUT : out std_logic;
         s_axis_s2mm_tdata : out std_logic_vector(31 downto 0);
         s_axis_s2mm_tlast : out std_logic;
         m_axis_mm2s_tready : out std_logic);                
end accel_wrapper;

architecture BEHAVE of accel_wrapper is                          
    signal GENERATED_VALID_OUT_0 : std_logic;
    signal ret_tdata : std_logic_vector(31 downto 0);                      
begin                          
VhdlComponent : entity work.apply                       
    port map(CLK => CLK,
             RST => RST,
             VALID_IN => VALID_IN,
             a => m_axis_mm2s_tdata,
             VALID_OUT => GENERATED_VALID_OUT_0,
             MODULE_OUT => ret_tdata); 

-- RETURN
VALID_OUT <= GENERATED_VALID_OUT_0;
s_axis_s2mm_tdata <= ret_tdata;
s_axis_s2mm_tlast <= m_axis_mm2s_tlast;
m_axis_mm2s_tready <= s_axis_s2mm_tready;                      
end BEHAVE;