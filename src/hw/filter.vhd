-------------------------------------------------------------------------------
-- Title      : Filter Module
-- Project    : 2d3dtof
--
-------------------------------------------------------------------------------
-- File       : filter.vhd
-- Author     : Florian Seibold, Nina Muehleis, Daniel Ziener, Bernhard Schmidt
-- Email      : bernhard.schmidt@informatik.uni-erlangen.de
-- Company    : Informatik 12
-- Created    : 2011-11-25
-- Last update: 2012-02-01
--
-------------------------------------------------------------------------------
-- Description:
--   This filter module can process a 2D filter operation on hd grayscale image 
--   and calculates the absolute values. The input and output signals have 
--   different bit widths.
--   
-------------------------------------------------------------------------------
-- GENERIC description:
--   - FILTERMATRIX   : 3x3 filter mask
--   - FILTER_SCALE   : scale factor of the filter mask 
--   - IMG_WIDTH      : image width
--   - IMG_HEIGHT     : image height
--   - IN_BITWIDTH    : bit width of the input signals
--   - OUT_BITWIDTH   : bit width of the output signal
--
-------------------------------------------------------------------------------
-- PORT description:
--
-- INPUTS:
--   - CLK           : input clock for the module
--   - RESET         : synchronous, high-active reset input
--   - DATA_IN       : input values, gray scale values in general
--   - H_SYNC_IN     : input hsync signal
--   - V_SYNC_IN     : input vsync signal
--
-- OUTPUTS: ( the output is delayed by 1 cycle)
--   - DATA_OUT      : filtered values, pixel
--   - H_SYNC_OUT    : output hsync signal
--   - V_SYNC_OUT    : output vsync signal
--
-------------------------------------------------------------------------------
-- LIMITATIONS:
--   - image width must be smaller than 2046
--   - only 3x3 filter masks are allowed
--   - region of values is limited, be careful! 
-------------------------------------------------------------------------------
-- Copyright (c) 2012 Informatik 12
-------------------------------------------------------------------------------
-- Changed 28.05.2012
-- Added output valid
-- Added process valid
-- Added fifo_data_count
-------------------------------------------------------------------------------

library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_unsigned.all;
use ieee.numeric_std.all;
use work.the_filter_package.all;

entity filter is
generic(
FILTERMATRIX   : filtMASK             := (0,0,0,0, 1, 0, 0, 0,0 );
FILTER_SCALE   : integer              := 16;
IN_BITWIDTH    : positive             := 12;
OUT_BITWIDTH   : positive             := 16
);
port(
CLK            : in  std_logic;
RESET          : in  std_logic;
IMG_WIDTH      : in  integer     := 1920;
IMG_HEIGHT     : in  integer     := 1080;
DATA_IN        : in  std_logic_vector(IN_BITWIDTH-1 downto 0);
H_SYNC_IN      : in  std_logic;
V_SYNC_IN      : in  std_logic;
DATA_OUT       : out std_logic_vector(OUT_BITWIDTH-1 downto 0);
H_SYNC_OUT     : out std_logic; -- um zwei Takte verzoegert
V_SYNC_OUT     : out std_logic;
VALID          : inout std_logic  := '0'
);
end entity filter;

architecture IMP of filter is

--------------------------------
--      FIFO    Component     --
--------------------------------
component bram_fifo is
generic (width, dept : integer);
port(
clk        : in  std_logic;
din        : in  std_logic_vector(width-1 downto 0);
rd_en      : in  std_logic;
rst        : in  std_logic;
wr_en      : in  std_logic;
data_count : out std_logic_vector(10 downto 0); --width-1
dout       : out std_logic_vector(width-1 downto 0);
empty      : out std_logic;
full       : out std_logic;
prog_full  : out std_logic
);
end component bram_fifo;

--------------------------
--      SIGNALS         --
--------------------------
-- Types 
-- constants

constant MAXFILTVAL : integer := (2 ** IN_BITWIDTH -1) *3;
constant MINFILTVAL : integer := (2 ** IN_BITWIDTH -1) * (-2);

constant FILTERSIZE : integer := 3;     -- filtersize (3x3)
constant SYNC_DELAY : positive:= 646;     -- for delay line
constant bpp        : integer := IN_BITWIDTH;    -- width of pixel fifos
constant fifo_size  : integer := 2048;  -- size of fifo

signal hsync_delay_line : std_logic_vector(SYNC_DELAY-1 downto 0) := (others => '0');
signal vsync_delay_line : std_logic_vector(SYNC_DELAY-1 downto 0) := (others => '0');

-- TYPES for FIFO SIGNALS
type filterarray is array (filtersize*filtersize-1 downto 0) of integer range MINFILTVAL to MAXFILTVAL;
type imagemask is array (filtersize*filtersize-1 downto 0) of std_logic_vector(IN_BITWIDTH-1 downto 0);
type fifo_io is array (filtersize-2 downto 0) of std_logic_vector(bpp-1 downto 0);
type fifo_data_count_type is array (filtersize-2 downto 0) of std_logic_vector(10 downto 0);
type valid_state is (SET_VALID, UNSET_VALID);

-- colors
constant BLACKx : std_logic_vector(IN_BITWIDTH-1 downto 0) := (others => '0');

-- FIFO SIGNALS
signal fifo_rd_en           : std_logic_vector(filtersize-2 downto 0) := (others => '0');
signal fifo_wr_en           : std_logic_vector(filtersize-2 downto 0) := (others => '0');
signal fifo_empty           : std_logic_vector(filtersize-2 downto 0);
signal fifo_data_in         : fifo_io;
signal fifo_data_out        : fifo_io;
signal fifo_data_count      : fifo_data_count_type;
signal fifo_valid_state     : valid_state := UNSET_VALID;

type state is (start_fl,in_fl, start_nl, in_nl, start_ll, in_ll, end_img);
signal next_state : state := start_fl;

signal pixelmatrix : imagemask;  
signal pfilt       : filterarray;

signal filtered_pixel     : std_logic_vector(OUT_BITWIDTH-1 downto 0);
signal datain             : std_logic_vector(IN_BITWIDTH-1 downto 0);
signal vertical_counter   : integer range 0 to 2047 := 0;  -- vertical image counter

signal data_inReg    : std_logic_vector(IN_BITWIDTH-1 downto 0);
signal data_inRegReg    : std_logic_vector(IN_BITWIDTH-1 downto 0);

signal process_pixel : std_logic := '0';
signal shift_pixel   : std_logic := '0';
signal sum_pixel     : std_logic := '0';
signal reinit        : std_logic := '0';
signal reset_fifo    : std_logic := '0';
signal new_img       : std_logic := '0';

signal hsync_reg : std_logic;
signal vsync_reg : std_logic;
signal hsync_regreg : std_logic;
signal vsync_regreg : std_logic;

signal valid_reg  : std_logic := '0';
signal h_sync_int : std_logic := '0';
signal v_sync_int : std_logic := '0';

type vsync_state_type is (UNSET_VSYNC, SET_VSYNC);
signal vsync_state : vsync_state_type := UNSET_VSYNC;
signal line_cnt : integer range 0 to 2048;
signal valid_rising_edge : std_logic := '0';
signal valid_falling_edge : std_logic := '0';


begin

-- ##########################################
--      Generate FIFOS                     
--      ==============                     
--      Number of FIFOs == Filter Size     
-- ##########################################


-- ######################################
-- 	PIXEL CLOCK
-- ###################################### 

FIFO_Data_Generation : for i in 0 to (filtersize-2) generate  -- two fifos are needed for a filter of 3x3
begin
dfifo : component bram_fifo
generic map(width => bpp, dept => fifo_size)
port map(
clk        => CLK,
din        => fifo_data_in(i),
rd_en      => fifo_rd_en(i),
rst        => reset_fifo,
wr_en      => fifo_wr_en(i),
data_count => fifo_data_count(i),
dout       => fifo_data_out(i),
empty      => fifo_empty(i),
full       => open,
prog_full  => open
);
end generate FIFO_Data_Generation;


pxl_CLK : process(CLK)
begin

if (CLK'event and CLK = '1') then
	
	shift_pixel <= process_pixel;
	sum_pixel <= shift_pixel;
	data_inReg      <= DATA_IN;
	data_inRegReg   <= data_inReg;
	
	hsync_reg <= H_SYNC_IN;
	vsync_reg <= V_SYNC_IN;
	
	hsync_regreg <= hsync_reg;
	vsync_regreg <= vsync_reg;
    
    valid_reg <= valid;
  --hsync_delay_line <= hsync_delay_line(SYNC_DELAY-2 downto 0) & H_SYNC_IN;
  --vsync_delay_line <= vsync_delay_line(SYNC_DELAY-2 downto 0) & V_SYNC_IN;
	 
end if;
end process pxl_CLK;


-- #####################################
--    general sync signals
---   ====================
--    This process writes the sync signals to a fifo and 
--    increases/decreases counters (vertical/horizontal)
--    Furthermore it triggers the start of writing/reading
--    the sync signals
-- #####################################

general_sync_signals : process(CLK, reset)
begin
if reinit = '1' then
	process_pixel      <='0';
  vertical_counter   <= 0;
  fifo_wr_en(0)      <='0';
	fifo_wr_en(1)      <='0';
  fifo_rd_en(0)      <='0';
	fifo_rd_en(1)      <='0';
	
	pixelmatrix(2) <= BLACKx;
	pixelmatrix(5) <= BLACKx;
	pixelmatrix(8) <= BLACKx;        
	next_state     <= start_fl;
	
elsif (CLK'event and CLK = '1') then

  process_pixel      <='0';
  vertical_counter   <= 0;
  fifo_wr_en(0)      <='0';
	fifo_wr_en(1)      <='0';
  fifo_rd_en(0)      <='0';
	fifo_rd_en(1)      <='0';
	
	pixelmatrix(2) <= BLACKx;
	pixelmatrix(5) <= BLACKx;
	pixelmatrix(8) <= BLACKx;
	new_img <= '0';

	case next_state is
		when start_fl => 
						
		if hsync_reg = '1' and vsync_reg = '1' then				
			vertical_counter   <=  vertical_counter +1;
			fifo_wr_en(0)   <= '1'; -- Randnuller
			fifo_wr_en(1)   <= '1';
			fifo_data_in(0) <= BLACKx; 
    		fifo_data_in(1) <= BLACKx;
    		next_state      <= in_fl;    
		end if;
		
		when in_fl =>
		  vertical_counter <=  vertical_counter;				
			fifo_wr_en(0)   <= '1'; -- Randnuller
			fifo_wr_en(1)   <= '1';
			fifo_data_in(0) <= BLACKx; 
		  fifo_data_in(1) <= data_inRegReg; 
			next_state      <= in_fl;
		  
			if hsync_regreg = '0' then
			  fifo_wr_en(0)   <= '1'; -- Randnulle
			  fifo_wr_en(1)   <= '1';
			  fifo_data_in(0) <= BLACKx; 
    		  fifo_data_in(1) <= BLACKx;
				next_state <= start_nl;				
			end if;
			
		when start_nl =>
		  vertical_counter <=  vertical_counter;
		  if (H_SYNC_IN = '1') and (V_SYNC_IN = '1') then 				
			  fifo_rd_en(0)      <= '1';
			  fifo_rd_en(1)      <= '1';
			  
			  if hsync_reg = '1' then
			     vertical_counter <=  vertical_counter + 1;
			     fifo_wr_en(0)   <= '1';
			     fifo_wr_en(1)   <= '1';
			     fifo_rd_en(0)   <= '1';
			     fifo_rd_en(1)   <= '1';
			     
			     fifo_data_in(0) <= fifo_data_out(1); 
  		       fifo_data_in(1) <= BLACKx;
			     
			     process_pixel   <= '1';
			     pixelmatrix(2) <= fifo_data_out(0);
			     pixelmatrix(5) <= fifo_data_out(1);
			     pixelmatrix(8) <= BLACKx;          
			     next_state <= in_nl;
			  end if;
			end if; 
			  
			  
		when in_nl =>
			
			vertical_counter <=  vertical_counter;     
			fifo_wr_en(0)      <= '1';
			fifo_wr_en(1)      <= '1';
			fifo_rd_en(0)      <= '1';
			fifo_rd_en(1)      <= '1';
			     
			fifo_data_in(0)    <= fifo_data_out(1); 
 		  fifo_data_in(1)    <= data_inRegReg;
			     
			process_pixel      <= '1';
			pixelmatrix(2)     <= fifo_data_out(0);
			pixelmatrix(5)     <= fifo_data_out(1);
			pixelmatrix(8)     <= data_inRegReg;
			
			if (hsync_reg = '0') then
			  fifo_rd_en(0)      <= '1';
			  fifo_rd_en(1)      <= '1';
			end if;	  		  
		  if hsync_regreg = '0' then
		    process_pixel      <= '0';
				fifo_wr_en(0)      <= '1';
			  fifo_wr_en(1)      <= '1';
			  fifo_rd_en(0)      <= '0';
			  fifo_rd_en(1)      <= '0';
			  fifo_data_in(0)    <= fifo_data_out(1); 
 		    fifo_data_in(1)    <= BLACKx;
			     
			  pixelmatrix(2)     <= fifo_data_out(0);
			  pixelmatrix(5)     <= fifo_data_out(1);
			  pixelmatrix(8)     <= BLACKx;
			  next_state         <= start_nl;
			  if vertical_counter = IMG_HEIGHT then
			     --next_state <= end_img;
			     next_state <= start_ll;
			  end if;
			end if;
			
	    when start_ll =>
	        fifo_wr_en(0)      <= '0';
            fifo_wr_en(1)      <= '0';
            fifo_rd_en(0)      <= '1';
            fifo_rd_en(1)      <= '1';
            
            next_state <= in_ll;
        
        when in_ll =>
            fifo_rd_en(0)      <= '1';
            fifo_rd_en(1)      <= '1';
                        
            pixelmatrix(2)     <= fifo_data_out(0);
            pixelmatrix(5)     <= fifo_data_out(1);
            pixelmatrix(8)     <= BLACKx;
            
            process_pixel      <= '1';
            
            if unsigned(fifo_data_count(filtersize-2)) = 1 then
                next_state <= end_img;
                process_pixel <= '0';
                fifo_rd_en(0)      <= '0';
                fifo_rd_en(1)      <= '0';
            end if;
	       
		when end_img =>
		  new_img <= '1';
		  next_state <= start_fl;
  end case;
end if;
end process general_sync_signals;


-- ##############################################
--    Generate Filter Processes 
-- 	multiply all components
-- ##############################################
filtergeneration : for i in 0 to filtersize*filtersize-1 generate
begin
filter_process : process(CLK)
begin
if (CLK = '1' and CLK'EVENT) then
    pfilt(i) <= to_integer(unsigned(pixelmatrix(i))) * filtermatrix(i);
end if;
end process filter_process;
end generate filtergeneration;


-- ##############################################
--      PROCESS pmproc
--      FILTERMATRIX --> pixel durchschieben!
-- ##############################################
pmproc : process (CLK)
begin

if (CLK = '1' and CLK'EVENT) then                                   
  if reinit = '1' or reset = '1' then -- initialize pixel
	   pixelmatrix(0) <= BLACKx;
	   pixelmatrix(1) <= BLACKx;
	       
	   pixelmatrix(3) <= BLACKx;
     pixelmatrix(4) <= BLACKx;

     pixelmatrix(6) <= BLACKx;
     pixelmatrix(7) <= BLACKx;
                
 	elsif process_pixel = '1' then -- process pixel
 	   pixelmatrix(0) <= pixelmatrix(1);
     pixelmatrix(1) <= pixelmatrix(2);

     pixelmatrix(3) <= pixelmatrix(4);
     pixelmatrix(4) <= pixelmatrix(5);
     
     pixelmatrix(6) <= pixelmatrix(7);
     pixelmatrix(7) <= pixelmatrix(8);
     
  end if;
end if;
end process pmproc;

-- #################################
-- ergebnis addieren
--      process msum
-- #################################
msum : process(CLK)
variable tmppfilt    : integer range 4*4095 downto -4*4095;
variable bv          : signed(OUT_BITWIDTH-1 downto 0);
begin 
if (CLK = '1' and CLK'EVENT) then 
    --valid <= '0';
                   
	if (sum_pixel = '1') then
	  tmppfilt := 0;
	                  
		-- add all        
		for k in 0 to filtersize*filtersize-1 loop
	     tmppfilt := tmppfilt + pfilt(k);
   	end loop;
    tmppfilt := tmppfilt/FILTER_SCALE; -- scale
   	bv	:= to_signed(tmppfilt, bv'length);
   	filtered_pixel <= std_logic_vector(bv); -- output
 
   	--valid <= '1';
 	else
 	  filtered_pixel <= (others => '1');
 	end if;
end if;
end process msum;

-- ##############################################
--      PROCESS proc_valid
--      Produces an output valid signal
-- ##############################################
proc_valid : process (CLK)
begin
if (CLK = '1' and CLK'EVENT) then
    case fifo_valid_state is
        when UNSET_VALID =>
            valid <= '0';
            
            if (sum_pixel = '1') then
                fifo_valid_state <= SET_VALID;
            end if;
        when SET_VALID =>
            valid <= '1';
            if (sum_pixel = '0') then
                valid <= '0';
                fifo_valid_state <= UNSET_VALID;
            end if;
    end case;
end if;
end process proc_valid;

-- ##############################################
--      PROCESS proc_vsync
--      Produces the vsync signal
-- ##############################################
proc_vsync : process (CLK)
--variable line_cnt : integer := 0;
begin
if (CLK = '1' and CLK'EVENT) then
    if reinit = '1' then
        v_sync_int <= '0';
        --valid_reg <= '0';
        line_cnt <= 0;
        vsync_state <= UNSET_VSYNC;
    else
        case vsync_state is
            when UNSET_VSYNC =>
                if valid = '1' and valid_reg = '0' and line_cnt = 0 then
                    v_sync_int <= '1';
                    vsync_state <= SET_VSYNC;
                end if;      
            when SET_VSYNC =>
                if valid = '0' and valid_reg = '1' then
                    line_cnt <= line_cnt + 1;
                    if line_cnt = IMG_HEIGHT - 1 then
                        v_sync_int <= '0';
                        vsync_state <= UNSET_VSYNC;
                    end if;
                end if; 
        end case;
    
    end if;
end if;
end process proc_vsync;

valid_rising_edge <= '1' when valid = '1' and valid_reg = '0' and line_cnt = 0 else '0';
valid_falling_edge <= '1' when valid = '0' and valid_reg = '1' and line_cnt = IMG_HEIGHT - 1 else '0';

V_SYNC_OUT <= (v_sync_int or valid_rising_edge) and (not valid_falling_edge);

proc_reset : process (CLK)
begin
if (CLK = '1' and CLK'EVENT) then
	reinit <= '0';
	if reset = '1' then
		reinit <= '1';
	end if;
end if;
end process;

proc_reset_fifo : process (CLK)
begin
if (CLK = '1' and CLK'EVENT) then
	reset_fifo <= '0';
	if new_img = '1' or reset = '1' then
		reset_fifo <= '1';
	end if;
end if;
end process;

				
DATA_OUT    <= filtered_pixel;
H_SYNC_OUT  <= hsync_delay_line(SYNC_DELAY-1);
--V_SYNC_OUT  <= v_sync_int;--vsync_delay_line(SYNC_DELAY-1);

end IMP;