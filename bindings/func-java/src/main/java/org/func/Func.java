package org.func;

import org.func.exceptions.FuncCommunicationException;

import java.util.List;
import java.util.Map;

/**
 * Copyright (C) 2008, Byte-Code srl <http://www.byte-code.com>
 * <p/>
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * <p/>
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * <p/>
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 * <p/>
 * Date: Jul 10, 2008
 * Time: 5:35:26 PM
 * 
 * @author Marco Mornati
 * @e-mail mmornati@byte-code.com
 * @version 1.0
 */
public interface Func {

    /**
     * Function invoked to optain the list of func client (machine that you can control in your java application using this API).
     * @return List of String with machine hostname
     */
    public List listMinions();

    /**
     * Caller for func-transmit with single client and no parameter
     * @param client Func client name. To invoke all defined clients use "*"
     * @param module Name of func module (use listModules to obtain the available modules)
     * @param method Name of method to invoke
     * @return Map with client name as key and func response as value
     * @throws FuncCommunicationException thrown if there is any kind of error in func invokation
     */
    public Map call (String client, String module, String method) throws FuncCommunicationException;

    /**
     * Caller for func-transmit with list of clients and no parameter
     * @param clients List of Func clients.
     * @param module Name of func module (use listModules to obtain the available modules)
     * @param method Name of method to invoke
     * @return Map with responses divided for each client: client name as key and func response as value
     * @throws FuncCommunicationException thrown if there is any kind of error in func invokation
     */
    public Map call (List clients, String module, String method) throws FuncCommunicationException;

    /**
     * Caller for func-transmit with single client and single parameter
     * @param client List of Func clients.
     * @param module Name of func module (use listModules to obtain the available modules)
     * @param method Name of method to invoke
     * @param parameter parameter to use with your method. Passed during func-transmit invokation
     * @return Map with responses divided for each client: client name as key and func response as value
     * @throws FuncCommunicationException thrown if there is any kind of error in func invokation
     */
    public Map call (String client, String module, String method, String parameter) throws FuncCommunicationException;

    /**
     * Func-Transmit Caller. It generates a Process to invoke func-transmit (using Yaml as default message) and then
     * it parses the output provided from func to generate a Map returned to your application.
     *
     * The Map content is something like this:
     *
     * [client_name1: func response for this client (could be a simple string, another map, ...),
     *  client_name2: func response]
     *
     * @param clients List of Func clients.
     * @param module Name of func module (use listModules to obtain the available modules)
     * @param method Name of method to invoke
     * @param parameters list of parameters to use with your method. Passed during func-transmit invokation
     * @return Map with responses divided for each client: client name as key and func response as value
     * @throws FuncCommunicationException thrown if there is any kind of error in func invokation
     */
    public Map call (List clients, String module, String method, List parameters) throws FuncCommunicationException;

    /**
     * Invoked to obtain for specified client the list of func module installed
     * 
     * @param client Name of the client to use with func. To invoke all defined clients use "*"
     * @return Map with clientName as key and list of all installed func module as object
     * @throws FuncCommunicationException thrown if there is any kind of error in func invokation
     */
    public Map listModules (String client) throws FuncCommunicationException;

    /**
     * Invoked to obtain for specified list of clients, the list of func module installed
     * @param clients List of func clients names.
     * @return Map with response divided for each client: clientName as key and list of all installed func module as value
     * @throws FuncCommunicationException thrown if there is any kind of error in func invokation
     */
    public Map listModules (List clients) throws FuncCommunicationException;

    /**
     * Invoked to obtain the list of methods for provided module and client
     * @param client client Name of the client to use with func. To invoke all defined clients use "*"
     * @param module name of func module for which you need a list of methods
     * @return Map with client name as key and list of module's methods as value
     * @throws FuncCommunicationException thrown if there is any kind of error in func invokation
     */
    public Map listModuleMethods (String client, String module) throws FuncCommunicationException;

    /**
     * Invoked to obtain the list of methods for provided module and list of clients
     * @param clients List of func clients names.
     * @param module name of func module for which you need a list of methods
     * @return Map with response divided for each client: clientName as key and list of all module's methods as value
     * @throws FuncCommunicationException thrown if there is any kind of error in func invokation
     */
    public Map listModuleMethods (List clients, String module) throws FuncCommunicationException;
    
}
