library ieee;
use ieee.std_logic_1164.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;


entity Bram_FIFO is
	generic (
			width :	integer := 32;
			dept  : integer := 256;
			set_prog_full_value : std_logic := '0';
			prog_full_value : integer := 0;
			set_empty_value : std_logic := '0';
			empty_value : std_logic_vector := x"abcdefab"
	);
  port (
			clk					: in  std_logic;
			din					: in  std_logic_vector(width-1 downto 0);
			rd_en				: in  std_logic;
			rst					: in  std_logic;
			wr_en				: in  std_logic;
			data_count	:	      OUT std_logic_VECTOR(10 downto 0);
			dout				: out std_logic_vector(width-1 downto 0);
			empty				: out std_logic;
			full				: out std_logic;
			prog_full 	: out std_logic
  );
end Bram_FIFO;

architecture Behavioral of Bram_FIFO is
  type bram_type is array (0 to dept-1) of std_logic_vector (width-1 downto 0);
  signal bram     				: bram_type; -- := (others => x"CDCDCDCD");	-- default value only for debug purpose
  signal read_ptr 				: integer range 0 to dept-1;
  signal write_ptr				: integer range 0 to dept-1;
  signal counter  				: integer range 0 to dept-1;
  signal read_data     		: std_logic_vector(width-1 downto 0);
  signal cache_data     	: std_logic_vector(width-1 downto 0);
  signal read_cache_data 	: std_logic;
  signal push     				: std_logic;
  signal pop      				: std_logic;
  signal sfull, sempty 		: std_logic;
begin
 data_count <= conv_std_logic_vector(counter, data_count'length);
 sempty <= '1' when counter = 0 else '0';
 sfull <= '1' when counter = dept else '0';
 empty <= sempty;
 full <= sfull;
 --IF PROG_FULL IS SET SET prog_full TO 1 WHEN MORE THAN prog_full_value VALUES ARE IN THE FIFO
 WITH_PROG_FULL_VALUE : if (set_prog_full_value = '1') generate
  prog_full <= '1' when counter >= prog_full_value else '0';
 end generate;
 
 --ENABLE WRITE REQEUST IF WRITE_EN IS SET AND EITHER THE FIFO IS NOT FULL (COUNTER = 1024) OR A READ IS PROCESSED IN THE SAME CLOCK
 push <= wr_en and (not sfull or rd_en);
 --ENABLE READ REQEUST IF READ_EN IS SET AND THE FIFO IS NOT EMPTY
 pop <= rd_en and not sempty;
 
  --BRAM READ WRITE LOGIC
  fifo_read_write: process (CLK) is 
  begin 
      if rising_edge(CLK) then 
       if (push = '1') then 
          bram(conv_integer(write_ptr)) <= din;
       end if;
			--if pop is selected read next value (read_ptr is raised with one clock delay and bram read operation needs one clock thus its required to read ahead)
			if (pop = '1') then
				read_data <= bram(conv_integer((read_ptr+1) mod dept));
			--otherwise read data at current read-pointer
			else
				read_data <= bram(conv_integer(read_ptr));
			end if;
      end if; 
  end process; 

  --BRAM READ WRITE LOGIC
  fifo_fwft: process (CLK) is 
  begin 
      if rising_edge(CLK) then 
			read_cache_data <= '0';
			if( pop = '1' and push = '1' and counter = 1 ) then
				cache_data <= din;
				read_cache_data <= '1';
		   --allow fwft one clock cycle after data is written when the fifo is empty
         elsif ( pop = '0' and sempty = '1' and push = '1' ) then
			 	cache_data <= din;
				read_cache_data <= '1';
			end if;
      end if; 
  end process; 
  
  --IF EMPTY_VALUE IS SET ENABLE OUTPUT OF THIS VALUE WHEN THE FIFO IS EMPTY
  WITH_EMPTY_VALUE : if (set_empty_value = '1') generate
	  dout <= empty_value when sempty = '1' else cache_data when read_cache_data = '1' else read_data;
  end generate;
  WITHOUT_EMPTY_VALUE : if (set_empty_value = '0') generate
	  dout <= cache_data when read_cache_data = '1' else read_data;
  end generate;
  
 --WIRTE/READ POINTER AND COUNTER LOGIC
 fifo_logic_proc : process(clk)
 begin
   if (clk'event AND clk='1') then
    if (rst = '1') then
      read_ptr <= 0;
      write_ptr <= 0;
      counter <= 0;
		
    else
      if(pop = '1') then
        --INCREASE READ POINTER 
        read_ptr <= (read_ptr+1) mod dept;
  		end if;
      
      if(push = '1') then
        --INCREASE WRITE POINTER ((write_ptr + 1) % 1024)
        write_ptr <= (write_ptr+1) mod dept;
      end if;
      --DECREASE FIFO FILL COUNTER WHEN ONLY POP INCREASE WHEN ONLY PUSH LEAVE OTHERWISE
      counter <= counter + conv_integer(push) - conv_integer(pop);
    end if;
   end if;
 end process;
end Behavioral;


