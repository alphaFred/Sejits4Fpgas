-- library ieee;
-- use ieee.std_logic_1164.all;
-- use ieee.std_logic_arith.all;
-- use IEEE.std_logic_unsigned.all;



-- some packacke to do these generic things the right way
package the_filter_package is

-- 	constant filter_size : integer 9; 
-- 
-- 		generic ( 
-- 						size : integer := 5;
-- 						width : integer := 6;
-- 						health : integer := 5
-- 			);
--		generic ( size_of_filter : integer := 3 );
		type filtMASK is array (8 downto 0) of integer range 20 downto -20;

end package the_filter_package;


