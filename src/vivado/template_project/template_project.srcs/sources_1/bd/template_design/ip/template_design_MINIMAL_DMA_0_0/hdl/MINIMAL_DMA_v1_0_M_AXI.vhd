library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity MINIMAL_DMA_v1_0_M_AXI is
	generic (
		-- Users to add parameters here
        LEN_WIDTH : integer := 16;
		-- User parameters ends
		-- Do not modify the parameters beyond this line


		-- Burst Length. Supports 1, 2, 4, 8, 16, 32, 64, 128, 256 burst lengths
		C_M_AXI_BURST_LEN	: integer	:= 16;
		-- Thread ID Width
		C_M_AXI_ID_WIDTH	: integer	:= 1;
		-- Width of Address Bus
		C_M_AXI_ADDR_WIDTH	: integer	:= 32;
		-- Width of Data Bus
		C_M_AXI_DATA_WIDTH	: integer	:= 32;
		-- Width of User Write Address Bus
		C_M_AXI_AWUSER_WIDTH	: integer	:= 0;
		-- Width of User Read Address Bus
		C_M_AXI_ARUSER_WIDTH	: integer	:= 0;
		-- Width of User Write Data Bus
		C_M_AXI_WUSER_WIDTH	: integer	:= 0;
		-- Width of User Read Data Bus
		C_M_AXI_RUSER_WIDTH	: integer	:= 0;
		-- Width of User Response Bus
		C_M_AXI_BUSER_WIDTH	: integer	:= 0
	);
	port (
		-- Users to add ports here
		out_data : out std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
        out_valid : out std_logic;
        out_last : out std_logic;
        out_ready : in std_logic;
        
        in_data : in std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
        in_valid : in std_logic;
        in_last : in std_logic := '0';
        in_ready : out std_logic;
        
        r_addr    : in std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0);
        r_len    : in std_logic_vector(LEN_WIDTH-1 downto 0);
        r_valid : in std_logic;
        r_ready : out std_logic;
        
        w_addr    : in std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0);
        w_len    : in std_logic_vector(LEN_WIDTH-1 downto 0);
        w_valid : in std_logic;
        w_ready : out std_logic;
        
        
        rst : in std_logic;
		-- User ports ends
		-- Do not modify the ports beyond this line
		
		
		
		-- Global Clock Signal.
		M_AXI_ACLK	: in std_logic;
		-- Global Reset Singal. This Signal is Active Low
		M_AXI_ARESETN	: in std_logic;
		-- Master Interface Write Address ID
		M_AXI_AWID	: out std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
		-- Master Interface Write Address
		M_AXI_AWADDR	: out std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0);
		-- Burst length. The burst length gives the exact number of transfers in a burst
		M_AXI_AWLEN	: out std_logic_vector(7 downto 0);
		-- Burst size. This signal indicates the size of each transfer in the burst
		M_AXI_AWSIZE	: out std_logic_vector(2 downto 0);
		-- Burst type. The burst type and the size information, 
    -- determine how the address for each transfer within the burst is calculated.
		M_AXI_AWBURST	: out std_logic_vector(1 downto 0);
		-- Lock type. Provides additional information about the
    -- atomic characteristics of the transfer.
		M_AXI_AWLOCK	: out std_logic;
		-- Memory type. This signal indicates how transactions
    -- are required to progress through a system.
		M_AXI_AWCACHE	: out std_logic_vector(3 downto 0);
		-- Protection type. This signal indicates the privilege
    -- and security level of the transaction, and whether
    -- the transaction is a data access or an instruction access.
		M_AXI_AWPROT	: out std_logic_vector(2 downto 0);
		-- Quality of Service, QoS identifier sent for each write transaction.
		M_AXI_AWQOS	: out std_logic_vector(3 downto 0);
		-- Optional User-defined signal in the write address channel.
		M_AXI_AWUSER	: out std_logic_vector(C_M_AXI_AWUSER_WIDTH-1 downto 0);
		-- Write address valid. This signal indicates that
    -- the channel is signaling valid write address and control information.
		M_AXI_AWVALID	: out std_logic;
		-- Write address ready. This signal indicates that
    -- the slave is ready to accept an address and associated control signals
		M_AXI_AWREADY	: in std_logic;
		-- Master Interface Write Data.
		M_AXI_WDATA	: out std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
		-- Write strobes. This signal indicates which byte
    -- lanes hold valid data. There is one write strobe
    -- bit for each eight bits of the write data bus.
		M_AXI_WSTRB	: out std_logic_vector(C_M_AXI_DATA_WIDTH/8-1 downto 0);
		-- Write last. This signal indicates the last transfer in a write burst.
		M_AXI_WLAST	: out std_logic;
		-- Optional User-defined signal in the write data channel.
		M_AXI_WUSER	: out std_logic_vector(C_M_AXI_WUSER_WIDTH-1 downto 0);
		-- Write valid. This signal indicates that valid write
    -- data and strobes are available
		M_AXI_WVALID	: out std_logic;
		-- Write ready. This signal indicates that the slave
    -- can accept the write data.
		M_AXI_WREADY	: in std_logic;
		-- Master Interface Write Response.
		M_AXI_BID	: in std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
		-- Write response. This signal indicates the status of the write transaction.
		M_AXI_BRESP	: in std_logic_vector(1 downto 0);
		-- Optional User-defined signal in the write response channel
		M_AXI_BUSER	: in std_logic_vector(C_M_AXI_BUSER_WIDTH-1 downto 0);
		-- Write response valid. This signal indicates that the
    -- channel is signaling a valid write response.
		M_AXI_BVALID	: in std_logic;
		-- Response ready. This signal indicates that the master
    -- can accept a write response.
		M_AXI_BREADY	: out std_logic;
		-- Master Interface Read Address.
		M_AXI_ARID	: out std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
		-- Read address. This signal indicates the initial
    -- address of a read burst transaction.
		M_AXI_ARADDR	: out std_logic_vector(C_M_AXI_ADDR_WIDTH-1 downto 0);
		-- Burst length. The burst length gives the exact number of transfers in a burst
		M_AXI_ARLEN	: out std_logic_vector(7 downto 0);
		-- Burst size. This signal indicates the size of each transfer in the burst
		M_AXI_ARSIZE	: out std_logic_vector(2 downto 0);
		-- Burst type. The burst type and the size information, 
    -- determine how the address for each transfer within the burst is calculated.
		M_AXI_ARBURST	: out std_logic_vector(1 downto 0);
		-- Lock type. Provides additional information about the
    -- atomic characteristics of the transfer.
		M_AXI_ARLOCK	: out std_logic;
		-- Memory type. This signal indicates how transactions
    -- are required to progress through a system.
		M_AXI_ARCACHE	: out std_logic_vector(3 downto 0);
		-- Protection type. This signal indicates the privilege
    -- and security level of the transaction, and whether
    -- the transaction is a data access or an instruction access.
		M_AXI_ARPROT	: out std_logic_vector(2 downto 0);
		-- Quality of Service, QoS identifier sent for each read transaction
		M_AXI_ARQOS	: out std_logic_vector(3 downto 0);
		-- Optional User-defined signal in the read address channel.
		M_AXI_ARUSER	: out std_logic_vector(C_M_AXI_ARUSER_WIDTH-1 downto 0);
		-- Write address valid. This signal indicates that
    -- the channel is signaling valid read address and control information
		M_AXI_ARVALID	: out std_logic;
		-- Read address ready. This signal indicates that
    -- the slave is ready to accept an address and associated control signals
		M_AXI_ARREADY	: in std_logic;
		-- Read ID tag. This signal is the identification tag
    -- for the read data group of signals generated by the slave.
		M_AXI_RID	: in std_logic_vector(C_M_AXI_ID_WIDTH-1 downto 0);
		-- Master Read Data
		M_AXI_RDATA	: in std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
		-- Read response. This signal indicates the status of the read transfer
		M_AXI_RRESP	: in std_logic_vector(1 downto 0);
		-- Read last. This signal indicates the last transfer in a read burst
		M_AXI_RLAST	: in std_logic;
		-- Optional User-defined signal in the read address channel.
		M_AXI_RUSER	: in std_logic_vector(C_M_AXI_RUSER_WIDTH-1 downto 0);
		-- Read valid. This signal indicates that the channel
    -- is signaling the required read data.
		M_AXI_RVALID	: in std_logic;
		-- Read ready. This signal indicates that the master can
    -- accept the read data and response information.
		M_AXI_RREADY	: out std_logic
	);
end MINIMAL_DMA_v1_0_M_AXI;

architecture implementation of MINIMAL_DMA_v1_0_M_AXI is


	-- function called clogb2 that returns an integer which has the
	--value of the ceiling of the log base 2

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


    constant BEAT_SHIFT : integer := clogb2(C_M_AXI_DATA_WIDTH/8)-1;
	-- C_TRANSACTIONS_NUM is the width of the index counter for
	-- number of beats in a burst write or burst read transaction.


	-- Example State machine to initialize counter, initialize write transactions, 
	 -- initialize read transactions and comparison of read data with the 
	 -- written data words.
	 type state is ( IDLE, ADDR,TRANSFER );
	 signal read_state  : state ;
	 signal write_state  : state ;

	-- AXI4FULL signals
	--AXI4 internal temp signals
	signal axi_awaddr	: unsigned(C_M_AXI_ADDR_WIDTH-1 downto 0);
	signal axi_awvalid	: std_logic;
	signal axi_wdata	: std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0) := (others => '0');
	signal axi_wlast	: std_logic;
	signal axi_wvalid	: std_logic;
	signal axi_bready	: std_logic;
	signal axi_araddr	: unsigned(C_M_AXI_ADDR_WIDTH-1 downto 0);
	signal axi_arvalid	: std_logic;
	signal axi_rready	: std_logic;

	
	--The burst counters are used to track the number of burst transfers of C_M_AXI_BURST_LEN burst length needed to transfer 2^C_MASTER_LENGTH bytes of data.
	signal start_single_burst_write	: std_logic;
	signal start_single_burst_read	: std_logic;
	signal writes_done	: std_logic;
	signal reads_done	: std_logic;



	signal read_mismatch	: std_logic;
	signal burst_write_active	: std_logic;
	signal burst_read_active	: std_logic;
	signal expected_rdata	: std_logic_vector(C_M_AXI_DATA_WIDTH-1 downto 0);
	--Interface response error flags
	signal write_resp_error	: std_logic;
	signal read_resp_error	: std_logic;
	signal wnext	: std_logic;
	signal rnext	: std_logic;


	signal write_index	: unsigned(7 downto 0);
	signal read_index	: unsigned(7 downto 0);

    signal axi_awlen    : unsigned(LEN_WIDTH-1 downto 0) := (others => '1');
    signal axi_arlen    : unsigned(LEN_WIDTH-1 downto 0) := (others => '1');
    
    signal s_m_axi_awlen    : unsigned(M_AXI_AWLEN'high downto 0);
    signal s_m_axi_arlen    : unsigned(M_AXI_ARLEN'high downto 0);   

begin
	-- I/O Connections assignments

	--I/O Connections. Write Address (AW)
	M_AXI_AWID	<= (others => '0');
	--The AXI address is a concatenation of the target base address + active offset range

	--Burst LENgth is number of transaction beats, minus 1

	--Size should be C_M_AXI_DATA_WIDTH, in 2^SIZE bytes, otherwise narrow bursts are used
	M_AXI_AWSIZE	<= std_logic_vector( to_unsigned(clogb2((C_M_AXI_DATA_WIDTH/8)-1), 3) );
	--INCR burst type is usually used, except for keyhole bursts
	M_AXI_AWBURST	<= "01";
	M_AXI_AWLOCK	<= '0';
	--Update value to 4'b0011 if coherent accesses to be used via the Zynq ACP port. Not Allocated, Modifiable, not Bufferable. Not Bufferable since this example is meant to test memory, not intermediate cache. 
	M_AXI_AWCACHE	<= "0010";
	M_AXI_AWPROT	<= "000";
	M_AXI_AWQOS	<= x"0";
	M_AXI_AWUSER	<= (others => '1');
	M_AXI_AWVALID	<= axi_awvalid;
	--Write Data(W)
	M_AXI_WDATA	<= axi_wdata;
	--All bursts are complete and aligned in this example
	M_AXI_WSTRB	<= (others => '1');
	M_AXI_WLAST	<= axi_wlast;
	M_AXI_WUSER	<= (others => '0');
	M_AXI_WVALID	<= axi_wvalid;
	--Write Response (B)
	M_AXI_BREADY	<= axi_bready;
	--Read Address (AR)
	M_AXI_ARID	<= (others => '0');

	--Burst LENgth is number of transaction beats, minus 1
	
	--Size should be C_M_AXI_DATA_WIDTH, in 2^n bytes, otherwise narrow bursts are used
	M_AXI_ARSIZE	<= std_logic_vector( to_unsigned( clogb2((C_M_AXI_DATA_WIDTH/8)-1),3 ));
	--INCR burst type is usually used, except for keyhole bursts
	M_AXI_ARBURST	<= "01";
	M_AXI_ARLOCK	<= '0';
	--Update value to 4'b0011 if coherent accesses to be used via the Zynq ACP port. Not Allocated, Modifiable, not Bufferable. Not Bufferable since this example is meant to test memory, not intermediate cache. 
	M_AXI_ARCACHE	<= "0010";
	M_AXI_ARPROT	<= "000";
	M_AXI_ARQOS	<= x"0";
	M_AXI_ARUSER	<= (others => '1');
	M_AXI_ARVALID	<= axi_arvalid;
	--Read and Read Response (R)
	M_AXI_RREADY	<= axi_rready;
	--Example design I/O


out_data <= M_AXI_RDATA;
out_valid <= M_AXI_RVALID and axi_rready;
out_last <= M_AXI_RLAST when (axi_arlen = (axi_arlen'range => '1')) else '0';--and M_AXI_RVALID and  axi_rready;
	----------------------
	--Write Address Channel
	----------------------

	-- The purpose of the write address channel is to request the address and 
	-- command information for the entire transaction.  It is a single beat
	-- of information.

	-- The AXI4 Write address channel in this example will continue to initiate
	-- write commands as fast as it is allowed by the slave/interconnect.
	-- The address will be incremented on each accepted address transaction,
	-- by burst_size_byte to point to the next address. 

	  process(M_AXI_ACLK)                                            
	  begin                                                                
	    if (rising_edge (M_AXI_ACLK)) then                                 
	      if (M_AXI_ARESETN = '0' or rst = '1') then 
	        axi_awvalid <= '0';                                            
	      else                                                             
	        -- If previously not valid , start next transaction            
	        if (axi_awvalid = '0' and start_single_burst_write = '1') then 
	          axi_awvalid <= '1';                                          
	          -- Once asserted, VALIDs cannot be deasserted, so axi_awvalid
	          -- must wait until transaction is accepted                   
	        elsif (M_AXI_AWREADY = '1' and axi_awvalid = '1') then         
	          axi_awvalid <= '0';                                          
	        else                                                           
	          axi_awvalid <= axi_awvalid;                                  
	        end if;                                                        
	      end if;                                                          
	    end if;                                                            
	  end process; 
	                                                          
  
        
    M_AXI_AWADDR	<= std_logic_vector(axi_awaddr);
    
    M_AXI_AWLEN <= std_logic_vector(s_m_axi_awlen);
    s_m_axi_awlen	<=  axi_awlen(s_m_axi_awlen'high downto 0)  when axi_awlen <  to_unsigned(C_M_AXI_BURST_LEN - 1, axi_awlen'length) else
                     to_unsigned(C_M_AXI_BURST_LEN - 1, s_m_axi_awlen'length);
                         

                                                      
	-- Next address after AWREADY indicates previous address acceptance    
	  process(M_AXI_ACLK)                                                  
	  begin                                                                
	    if (rising_edge (M_AXI_ACLK)) then                                 
	      if (M_AXI_ARESETN = '0' or rst = '1' or (w_valid = '1' and writes_done = '1')) then                                   
	       axi_awaddr <= unsigned(w_addr); 
	       axi_awlen <= unsigned(w_len);
	      else                                                             
	        if (M_AXI_AWREADY= '1' and axi_awvalid = '1') then             
	          axi_awaddr <= axi_awaddr + shift_left(resize(resize(s_m_axi_awlen,s_m_axi_awlen'length+1)+1,axi_awaddr'length), BEAT_SHIFT); --check if multiplier is used - sll would be good  
	          axi_awlen <= axi_awlen - ( resize(s_m_axi_awlen,axi_awlen'length)+1);
	        end if;                                                        
	      end if;                                                          
	    end if;                                                            
	  end process;                                                         


	----------------------
	--Write Data Channel
	----------------------

	--The write data will continually try to push write data across the interface.

	--The amount of data accepted will depend on the AXI slave and the AXI
	--Interconnect settings, such as if there are FIFOs enabled in interconnect.

	--Note that there is no explicit timing relationship to the write address channel.
	--The write channel has its own throttling flag, separate from the AW channel.

	--Synchronization between the channels must be determined by the user.

	--The simpliest but lowest performance would be to only issue one address write
	--and write data burst at a time.

	--In this example they are kept in sync by using the same address increment
	--and burst sizes. Then the AW and W channels have their transactions measured
	--with threshold counters as part of the user logic, to make sure neither 
	--channel gets too far ahead of each other.

	--Forward movement occurs when the write channel is valid and ready

	  wnext <= M_AXI_WREADY and axi_wvalid;                                       
	                                                                                    
	-- WVALID logic, similar to the axi_awvalid always block above                      
	  process(M_AXI_ACLK)                                                               
	  begin                                                                             
	    if (rising_edge (M_AXI_ACLK)) then                                              
	      if (M_AXI_ARESETN = '0' or rst = '1') then                                                
	        axi_wvalid <= '0';                                                          
	      else                                                                          
	        if (axi_wvalid = '0' and M_AXI_AWREADY= '1' and axi_awvalid = '1') then --start_single_burst_write = '1') then               
	          -- If previously not valid, start next transaction                        
	          axi_wvalid <= '1';                                                        
	          --     /* If WREADY and too many writes, throttle WVALID                  
	          --      Once asserted, VALIDs cannot be deasserted, so WVALID             
	          --      must wait until burst is complete with WLAST */                   
	        elsif (wnext = '1' and axi_wlast = '1') then                                
	          axi_wvalid <= '0';                                                        
	        else                                                                        
	          axi_wvalid <= axi_wvalid;                                                 
	        end if;                                                                     
	      end if;                                                                       
	    end if;                                                                         
	  end process;                                                                      
	                                                                                    
                                                         
	-- Burst length counter. Uses extra counter register bit to indicate terminal       
	-- count to reduce decode logic */                                                  
	  process(M_AXI_ACLK)                                                               
	  begin                                                                             
	    if (rising_edge (M_AXI_ACLK)) then                                              
	      if (M_AXI_ARESETN = '0' or start_single_burst_write = '1' or rst = '1') then               
	        write_index <= (others => '0');
	        axi_wlast <= '0';                                           
	      else                                                                     
	        if (wnext = '1' and write_index /= to_unsigned(0,write_index'length)) then                
	           write_index <= write_index - 1;
	           if(write_index = to_unsigned(1,write_index'length)) then
	               axi_wlast <= '1';
	           else
	               axi_wlast <= '0';
	           end if;
	        elsif (wnext = '1' and write_index = to_unsigned(0,write_index'length)) then  
	           axi_wlast <= '0';
	        elsif ( M_AXI_AWREADY= '1' and axi_awvalid = '1' ) then
	           write_index <= s_m_axi_awlen;
	           if ( s_m_axi_awlen = to_unsigned(0,s_m_axi_awlen'length)) then
	               axi_wlast <= '1';
	           else
	               axi_wlast <= '0';
	           end if;
	        end if;                                                                     
	      end if;                                                                       
	    end if;                                                                         
	  end process;                                                                      
	                                                                                    
	-- Write Data Generator                                                             
	-- Data pattern is only a simple incrementing count from 0 for each burst  */       
--	  process(M_AXI_ACLK)                                                               
--	  variable  sig_one : integer := 1;                                                 
--	  begin                                                                             
--	    if (rising_edge (M_AXI_ACLK)) then       
--	       axi_wdata <= axi_wdata;--in_data;
	       
--	       if(wnext = '1') then
--	       axi_wdata <= std_logic_vector(unsigned(axi_wdata)+1);--in_data;
--	       end if;
	       
--	    end if;                                                                         
--	  end process;                                                                      
    in_ready <= wnext;
    axi_wdata <= in_data;

	------------------------------
	--Write Response (B) Channel
	------------------------------

	--The write response channel provides feedback that the write has committed
	--to memory. BREADY will occur when all of the data and the write address
	--has arrived and been accepted by the slave.

	--The write issuance (number of outstanding write addresses) is started by 
	--the Address Write transfer, and is completed by a BREADY/BRESP.

	--While negating BREADY will eventually throttle the AWREADY signal, 
	--it is best not to throttle the whole data channel this way.

	--The BRESP bit [1] is used indicate any errors from the interconnect or
	--slave for the entire write burst. This example will capture the error 
	--into the ERROR output. 

	  process(M_AXI_ACLK)                                             
	  begin                                                                 
	    if (rising_edge (M_AXI_ACLK)) then                                  
	      if (M_AXI_ARESETN = '0' or rst = '1') then                                    
	        axi_bready <= '0';                                              
	        -- accept/acknowledge bresp with axi_bready by the master       
	        -- when M_AXI_BVALID is asserted by slave                       
	      else                                                              
	        if (M_AXI_BVALID = '1' and axi_bready = '0') then               
	          axi_bready <= '1';                                            
	          -- deassert after one clock cycle                             
	        elsif (axi_bready = '1') then                                   
	          axi_bready <= '0';                                            
	        end if;                                                         
	      end if;                                                           
	    end if;                                                             
	  end process;                                                          
	                                                                        
	                                                                        
	--Flag any write response errors                                        
	  write_resp_error <= axi_bready and M_AXI_BVALID and M_AXI_BRESP(1);   


	------------------------------
	--Read Address Channel
	------------------------------

	--The Read Address Channel (AW) provides a similar function to the
	--Write Address channel- to provide the tranfer qualifiers for the burst.

	--In this example, the read address increments in the same
	--manner as the write address channel.

	  process(M_AXI_ACLK)										  
	  begin                                                              
	    if (rising_edge (M_AXI_ACLK)) then                               
	      if (M_AXI_ARESETN = '0' or rst = '1') then                                 
	        axi_arvalid <= '0';                                          
	     -- If previously not valid , start next transaction             
	      else                                                           
	        if (axi_arvalid = '0' and start_single_burst_read = '1') then
	          axi_arvalid <= '1';                                        
	        elsif (M_AXI_ARREADY = '1' and axi_arvalid = '1') then       
	          axi_arvalid <= '0';                                        
	        end if;                                                      
	      end if;                                                        
	    end if;                                                          
	  end process;                                                       


                       
    M_AXI_ARADDR	<= std_logic_vector(axi_araddr);

 M_AXI_ARLEN	<=  std_logic_vector(s_m_axi_arlen);

   s_m_axi_arlen	<= axi_arlen(s_m_axi_arlen'high downto 0)  when axi_arlen <  to_unsigned(C_M_AXI_BURST_LEN - 1, axi_arlen'length) else
                          to_unsigned(C_M_AXI_BURST_LEN - 1, s_m_axi_arlen'length);                                                                     
	-- Next address after ARREADY indicates previous address acceptance  
	  process(M_AXI_ACLK)                                                
	  begin                                                              
	    if (rising_edge (M_AXI_ACLK)) then                               
	      if (M_AXI_ARESETN = '0' or rst = '1' or (r_valid = '1' and reads_done = '1')) then                                 
	        axi_araddr <= unsigned(r_addr); 
	        axi_arlen <= unsigned(r_len);                              
	      else                                                           
	        if (M_AXI_ARREADY = '1' and axi_arvalid = '1') then          
	          axi_araddr <= axi_araddr + shift_left(resize(resize(s_m_axi_arlen,s_m_axi_arlen'length+1)+1,axi_araddr'length), BEAT_SHIFT);  -- resize +1 -> +1 -> resize 32 -> shift
	          axi_arlen <= axi_arlen - (resize(s_m_axi_arlen,axi_arlen'length)+1);          
	        end if;                                                      
	      end if;                                                        
	    end if;                                                          
	  end process;                                                       


	----------------------------------
	--Read Data (and Response) Channel
	----------------------------------

	                                                                        
	--/*                                                                    
	-- The Read Data channel returns the results of the read request        
	--                                                                      
	-- In this example the data checker is always able to accept            
	-- more data, so no need to throttle the RREADY signal                  
	-- */                                                                   
	  process(M_AXI_ACLK)                                                   
	  begin                                                                 
	    if (rising_edge (M_AXI_ACLK)) then                                  
	      if (M_AXI_ARESETN = '0' or rst = '1') then             
	        axi_rready <= '0';                                              
	     -- accept/acknowledge rdata/rresp with axi_rready by the master    
	      -- when M_AXI_RVALID is asserted by slave                         
	      else                                                   
	        if (M_AXI_RVALID = '1') then                         
	          if (M_AXI_RLAST = '1' and axi_rready = '1') then   
	            axi_rready <= '0';                               
	           else                                              
	             axi_rready <= '1';                              
	          end if;                                            
	        end if;                                              
	      end if;                                                
	    end if;                                                  
	  end process;                                               
	                                                                        
  
	                                                                        
	--Flag any read response errors                                         
	  read_resp_error <= axi_rready and M_AXI_RVALID and M_AXI_RRESP(1);    



	  r_ready <= reads_done;
	     
	     
READ_PROC: process
begin
	wait until rising_edge(M_AXI_ACLK);
	   if (M_AXI_ARESETN = '0' or rst = '1') then
	       read_state     <= IDLE;                                                                                                                                  
           start_single_burst_read  <= '0';   
           reads_done <= '1';                                                               
	   else
           case(read_state) is
           when IDLE => 
                if(r_valid = '1' and reads_done = '1') then
                    read_state <= ADDR;
                    reads_done <= '0';
                else
                    read_state <= IDLE;
                    reads_done <= '1';
                end if;

           when ADDR =>
                if (M_AXI_RVALID = '1' and axi_rready = '1' and M_AXI_RLAST = '1' and (axi_arlen = (axi_arlen'range => '1'))) then                                                                   
                    read_state <= IDLE;                                                            
                else                                                                                         
                    read_state  <= ADDR;                                                              
                                                                                              
                    if (axi_arvalid = '0' and burst_read_active = '0' and start_single_burst_read = '0' and out_ready = '1') then    
                        start_single_burst_read <= '1';                                                            
                    else                                                                                         
                        start_single_burst_read <= '0'; --Negate to generate a pulse                               
                    end if;
                end if;
                        
	       when others  =>                                                                                  
                read_state  <= IDLE;  
      end case;
	      
    end if;
end process;                                                                                                           
	                                                                                                             
w_ready <= writes_done; 
 	     
WRITE_PROC: process
   begin
        wait until rising_edge(M_AXI_ACLK);
             if (M_AXI_ARESETN = '0'  or rst = '1') then
               write_state     <= IDLE;                                                                                                                                  
             start_single_burst_write  <= '0';
             writes_done <= '1';                                                                       
       else
             case(write_state) is
                 when IDLE => 
                     if(w_valid = '1' and writes_done = '1') then
                         write_state <= ADDR;
                         writes_done <= '0';  
                     else
                         writes_done <= '1';
                         write_state <= IDLE;
                     end if;
                 when ADDR =>
                     if (M_AXI_BVALID = '1' and (axi_awlen = (axi_awlen'range => '1')) and axi_bready = '1') then
                         -- writes_done <= '1';                                                                 
                         write_state <= IDLE;                                                            
                     else                                                                                         
                         write_state  <= ADDR;                                                              
                                                                                         
                         if (axi_awvalid = '0' and start_single_burst_write = '0' and burst_write_active = '0'  and in_valid = '1') then 
                             start_single_burst_write <= '1';                                                            
                         else                                                                                         
                             start_single_burst_write <= '0'; --Negate to generate a pulse                               
                         end if;
                     end if;
                     
                when others  =>                                                                                  
                         write_state  <= IDLE;  
             end case;
       
       end if;
   end process;                                                                                    
                                                              
	                                                                                                             
	                                                                                                             
	  -- burst_write_active signal is asserted when there is a burst write transaction                           
	  -- is initiated by the assertion of start_single_burst_write. burst_write_active                           
	  -- signal remains asserted until the burst write is accepted by the slave                                  
	  process(M_AXI_ACLK)                                                                                        
	  begin                                                                                                      
	    if (rising_edge (M_AXI_ACLK)) then                                                                       
	      if (M_AXI_ARESETN = '0' or rst = '1') then                                                                         
	        burst_write_active <= '0';                                                                           
	                                                                                                             
	       --The burst_write_active is asserted when a write burst transaction is initiated                      
	      else                                                                                                   
	        if (start_single_burst_write = '1') then                                                             
	          burst_write_active <= '1';                                                                         
	        elsif (M_AXI_BVALID = '1' and axi_bready = '1') then                                                 
	          burst_write_active <= '0';                                                                         
	        end if;                                                                                              
	      end if;                                                                                                
	    end if;                                                                                                  
	  end process;                                                                                               
	                                                                                                             
	 -- Check for last write completion.                                                                         
	                                                                                                             
	  -- burst_read_active signal is asserted when there is a burst write transaction                            
	  -- is initiated by the assertion of start_single_burst_write. start_single_burst_read                      
	  -- signal remains asserted until the burst read is accepted by the master                                  
	  process(M_AXI_ACLK)                                                                                        
	  begin                                                                                                      
	    if (rising_edge (M_AXI_ACLK)) then                                                                       
	      if (M_AXI_ARESETN = '0' or rst = '1') then                                                                         
	        burst_read_active <= '0';                                                                            
	                                                                                                             
	       --The burst_write_active is asserted when a write burst transaction is initiated                      
	      else                                                                                                   
	        if (start_single_burst_read = '1')then                                                               
	          burst_read_active <= '1';                                                                          
	        elsif (M_AXI_RVALID = '1' and axi_rready = '1' and M_AXI_RLAST = '1') then                           
	          burst_read_active <= '0';                                                                          
	        end if;                                                                                              
	      end if;                                                                                                
	    end if;                                                                                                  
	  end process;                                                                                               
	                                                                                                             
                                                                                             

	-- Add user logic here

	-- User logic ends

end implementation;