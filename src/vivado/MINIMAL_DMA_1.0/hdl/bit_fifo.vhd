----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 04/19/2016 05:57:44 PM
-- Design Name: 
-- Module Name: bit_fifo - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity bit_fifo is
    Generic (
    WIDTH : integer := 1;
    DEPTH : integer := 2
    );
    Port ( clk : in STD_LOGIC;
           rst : in STD_LOGIC;
           in_valid : in STD_LOGIC;
           in_data : in STD_LOGIC_VECTOR(WIDTH-1 downto 0);
           in_ready : out STD_LOGIC;
           out_ready : in STD_LOGIC;
           out_valid : out STD_LOGIC;
           out_data : out STD_LOGIC_VECTOR(WIDTH-1 downto 0)
           );
end bit_fifo;

architecture Behavioral of bit_fifo is

	function clogb2 (bit_depth : integer) return integer is            
	 	variable depth  : integer := bit_depth;                               
	 	variable count  : integer := 1;                                       
	 begin                                                                   
	 	 for clogb2 in 1 to bit_depth loop  -- Works for up to 32 bit integers
	      if (bit_depth <= 2) then                                           
	        count := 1;                                                      
	      else                                                               
	        if(depth <= 1) then                                              
	 	       count := count;                                                
	 	     else                                                             
	 	       depth := depth / 2;                                            
	          count := count + 1;                                            
	 	     end if;                                                          
	 	   end if;                                                            
	   end loop;                                                             
	   return(count);        	                                              
	 end;
	 
	 
constant PTR_WIDTH : integer := clogb2(DEPTH);

type store_type is array(DEPTH-1 downto 0) of std_logic_vector(WIDTH-1 downto 0);
signal store : store_type;

signal r_ptr : unsigned(PTR_WIDTH-1 downto 0) := to_unsigned(0,PTR_WIDTH);
signal w_ptr : unsigned(PTR_WIDTH-1 downto 0) := to_unsigned(0,PTR_WIDTH);

signal cnt : unsigned(PTR_WIDTH downto 0) := to_unsigned(0,PTR_WIDTH+1);

begin


out_data <= store(to_integer(r_ptr));
out_valid <= (not rst) when cnt > to_unsigned(0,cnt'length) else '0';

--in_ready <= '0' when (cnt = to_unsigned(DEPTH,cnt'length)) or ((cnt = to_unsigned(DEPTH-1,cnt'length)) and in_valid = '1')  else '1';
in_ready <= '1' when (cnt /= to_unsigned(DEPTH,cnt'length))  else '0';



fifo_proc: process
variable vcnt : unsigned(cnt'range);
begin

    wait until rising_edge(clk);
    
    if(rst = '1') then
        r_ptr <= to_unsigned(0,r_ptr'length);
        w_ptr <= to_unsigned(0,w_ptr'length);
        cnt <= to_unsigned(0,cnt'length);
    else
        vcnt := cnt;
        if(in_valid = '1' and (cnt /= to_unsigned(DEPTH,cnt'length))) then
            store(to_integer(w_ptr)) <= in_data;
            vcnt := vcnt+1;
            if(w_ptr = to_unsigned(DEPTH-1,w_ptr'length)) then
                w_ptr <= to_unsigned(0,w_ptr'length);
            else
                w_ptr <= w_ptr+1;
            end if;
        end if;
        
        if(out_ready = '1' and (cnt > to_unsigned(0,cnt'length))) then
            if(r_ptr = to_unsigned(DEPTH-1,r_ptr'length)) then
                r_ptr <= to_unsigned(0,r_ptr'length);
            else
                r_ptr <= r_ptr +1;
            end if;
            vcnt := vcnt -1;
        end if;
        
        cnt <= vcnt;
        
        
    end if;

end process;

end Behavioral;
