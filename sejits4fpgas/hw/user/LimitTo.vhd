library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
use IEEE.NUMERIC_STD.ALL;

library UNISIM;
use UNISIM.VComponents.all;


entity LimitTo is
    Generic(
        VALID_BITS      : positive := 255
        );
    Port (
        CLK             : in  std_logic;
        RST             : in  std_logic; -- low active
        VALID_IN        : in  std_logic; -- high active
        READY_IN        : in  std_logic;
        DATA_IN         : in  std_logic_vector(31 downto 0);
        VALID_OUT       : out std_logic; -- high active
        READY_OUT       : out std_logic;
        DATA_OUT        : out std_logic_vector(31 downto 0)
        );
end LimitTo;

architecture limit_to_behave of LimitTo is
begin

    Compare :process(CLK)
    begin
        if RST = '1' then
            DATA_OUT <= (31 downto 0 => '0');
            VALID_OUT <= '0';
            READY_OUT <= '0';
        elsif(rising_edge(CLK)) then
            if VALID_BITS < signed(DATA_IN) then
                DATA_OUT <= std_logic_vector(to_unsigned(VALID_BITS, DATA_OUT'length));
            elsif signed(DATA_IN) < 0 then
                DATA_OUT <= (DATA_OUT'length-1 downto 0 => '0');
            else
                DATA_OUT <= DATA_IN;
            end if;
            VALID_OUT <= VALID_IN;
            READY_OUT <= READY_IN;
        end if;
     end process;

--    slice_full: if VALID_BITS >= 32 generate
--    begin
--        DATA_OUT <= DATA_IN;
--    end generate slice_full;

--    slice_limit: if VALID_BITS < 32 generate
--    begin
--        DATA_OUT <= (31 downto VALID_BITS => '0') & DATA_IN(VALID_BITS-1 downto 0);
--    end generate slice_limit;
end limit_to_behave;
