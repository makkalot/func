package org.func

import org.func.exceptions.FuncCommunicationException
import org.jvyaml.YAML
import org.func.exceptions.CertmasterException

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
 * Date: Jul 10, 2008
 * Time: 5:38:02 PM
 *
 * @author Marco Mornati
 * @e-mail mmornati@byte-code.com 
 * @version 1.0
 */
class FuncImpl implements Func {

    private funcTransmit = "func-transmit"
    private func = "func"

    public FuncImpl() {

    }

    public FuncImpl(String transmit) {
        this.funcTransmit = transmit
    }

    public Map call(String client, String module, String method) throws FuncCommunicationException {
        this.call([client], module, method, null)
    }

    public Map call(List clients, String module, String method) throws FuncCommunicationException {
        this.call(clients, module, method, null)
    }

    public Map call(String client, String module, String method, String parameter) throws FuncCommunicationException {
        this.call([client], module, method, [parameter])
    }

    public Map call(List clients, String module, String method, List parameters) throws FuncCommunicationException {
        return funcCall(clients, module, method, parameters)
    }

    public Map listModules(String client) {
        return this.listModules([client])
    }

    public Map listModuleMethods(String client, String method) {
        return this.listModuleMethods([client], method)
    }

    public Map listModules(List clients) {
        return funcCall(clients, "system", "list_modules", null)
    }

    public Map listModuleMethods(List clients, String module) {
        return funcCall(clients, module, "list_methods", null)
    }


    public List listMinions() {
        def minions = []
        def commandToExecute = [func, "*", "list_minions"]
        def proc = commandToExecute.execute()
        proc.waitFor()
        def procAnswer = proc.text
        if (procAnswer) {
            minions = procAnswer.split("\n")
        } else {
            throw new CertmasterException("Error communicating with certmaster")
        }
        return minions;
    }


    private Map funcCall(List clients, String module, String method, List parameters) throws FuncCommunicationException {
        def values = [clients: clientsCallPatch(clients), module: module, method: method, parameters: parameters]
        def yamlDump = YAML.dump(values)
        def commandToExecute = [funcTransmit]
        def proc = commandToExecute.execute()
        proc.withWriter {writer -> writer << yamlDump }
        proc.waitFor()
        def procAnswer = proc.text
        Map funcResponse = null
        if (procAnswer) {
            def response = YAML.load(procAnswer)
            if (response instanceof Map) {
                funcResponse = (Map) response
            }
        } else {
            throw new FuncCommunicationException(procAnswer + " - Error reading answer from Func-Transmit Process!")
        }
        return funcResponse
    }


    private String clientsCallPatch(List clients) {
        //TODO: Now Func does not accept a LIST of client (you can send a list with a string formatted like client1;client2;client
        //TODO: Change this patch when func will be ready
        //===== PATCH BEGINS
        String clientToSend = ""
        clients?.each {
            if (!clientToSend.equals("")) {
                clientToSend += ";"
            }
            clientToSend += "${it}"
        }
        return clientToSend
        //===== PATCH ENDS
    }

    public void setFuncTransmit(String funcTransmit) {
        this.funcTransmit = funcTransmit
    }

    public String getFuncTransmit() {
        return funcTransmit
    }

}