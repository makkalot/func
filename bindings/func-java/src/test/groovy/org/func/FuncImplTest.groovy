package org.func

import org.jvyaml.YAML

/**
 *  Copyright (C) 2008, Byte-Code srl <http://www.byte-code.com>
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
 * Date: Jul 11, 2008
 * Time: 10:30:47 AM
 *
 * @author Marco Mornati
 * @e-mail mmornati@byte-code.com
 * @version 1.0
 * 
 */
class FuncImplTest extends GroovyTestCase {

    void testCall() {
        Func func = FuncFactory.getFunc("/home/mmornati/projects/func/scripts/func-transmit")
        def response = func.call ("*", "hardware", "info")
        assertTrue ("Func Response is not a Map", response instanceof Map)
    }

    void testListModules() {
        Func func = FuncFactory.getFunc("/home/mmornati/projects/func/scripts/func-transmit")
        def response = func.listModules("bcmmornati")
        assertTrue ("Func Response is not a Map", response instanceof Map)
    }

    void testListModuleMethods() {
        Func func = FuncFactory.getFunc("/home/mmornati/projects/func/scripts/func-transmit")
        def response = func.listModuleMethods("bcmmornati", "hardware")
        assertTrue ("Func Response is not a Map", response instanceof Map)
    }

    void testClientPatch() {
        def clients = ["client1", "client2"]
        FuncImpl func = FuncFactory.getFunc()
        def returned = func.clientsCallPatch(clients)
        assertEquals ("Error in ClientsPatch generation", returned, "client1;client2")
    }

    void testListMinions() {
        Func func = FuncFactory.getFunc()
        def response = func.listMinions()
        assertTrue ("Error in calling listMinions", response instanceof List)
    }

}