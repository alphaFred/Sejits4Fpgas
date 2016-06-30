----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 07/29/2015 12:03:12 PM
-- Design Name: 
-- Module Name: dsp_sreg_block - Behavioral
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
use IEEE.NUMERIC_STD.ALL;


entity dsp_sreg_block is
    Generic (
        WIDTH   : natural;
        LENGTH  : natural
    );
    Port (
        D   : in STD_LOGIC_VECTOR (WIDTH-1 downto 0);
        CLK : in STD_LOGIC;
        RST : in STD_LOGIC;
        Q   : out STD_LOGIC_VECTOR (WIDTH-1 downto 0)
    );
end dsp_sreg_block;

architecture Behavioral of dsp_sreg_block is
    
    TYPE iBus is array(LENGTH-1 downto 0) of std_logic_vector(WIDTH-1 downto 0);
    
    signal sRegBus : iBus;
    
    COMPONENT dsp_dff_block
        Generic (
            WIDTH : natural
        );
        Port (
            D   : in STD_LOGIC_VECTOR (WIDTH-1 downto 0);
            CLK : in STD_LOGIC;
            RST : in STD_LOGIC;
            Q   : out STD_LOGIC_VECTOR (WIDTH-1 downto 0)
        );        
    END COMPONENT;
begin
    shiftReg: for i in 1 to LENGTH generate
    begin
        dffLeft: if i = 1 generate
        begin
            dff: component dsp_dff_block
                generic map (
                    WIDTH => WIDTH
                )
                port map (
                    D => D,
                    CLK => CLK,
                    RST => RST,
                    Q => sRegBus(i)
                );
        end generate dffLeft;
        --
        dffOthers: if (i > 1 AND i < LENGTH) generate
        begin
            dff: component dsp_dff_block
                generic map (
                    WIDTH => WIDTH)
                port map (
                    D => sRegBus(i-1),
                    CLK => CLK,
                    RST => RST,
                    Q => sRegBus(i)
                );
        end generate dffOthers;
        --
        dffRight: if i = LENGTH generate
        begin
            dff: component dsp_dff_block
                generic map (
                    WIDTH => WIDTH)
                port map (
                    D => sRegBus(i-1),
                    CLK => CLK,
                    RST => RST,
                    Q => Q
                );
        end generate dffRight;            
    end generate shiftReg;
end architecture Behavioral;
