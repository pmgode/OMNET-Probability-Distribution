//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
//

simple txc1
{
    parameters:
        volatile double delayTime @unit(s);
        @display("i=block/routing");

        @signal[arrival](type="long");
        @statistic[intarrTime](title="inter arrival time"; source="arrival"; record=vector,stats; interpolationmode=none);

    gates:
        input in;
        output out;
}

network Ex2
{
    @display("bgb=311,262");
    submodules:
        S: txc1 {
            parameters:
                @display("i=,cyan");
        }
        R: txc1 {
            parameters:
                @display("i=,gold;p=123,193");
        }

    connections:
        S.out --> R.in; //{  delay = 100ms; } --> R.in;
         R.out --> S.in; //{delay=100ms;} --> S.in;  
}