import org.func.FuncImpl

class FuncGrailsPlugin {
    def version = 1.0
    def dependsOn = [:]

    def author = "Marco Mornati"
    def authorEmail = "mmornati@byte-code.com"
    def title = "Plugin to make your application ables to call Func (https://fedorahosted.org/func)"

    // URL to the plugin's documentation
    def documentation = "http://grails.org/FuncGrailsPlugin+Plugin"

    def doWithSpring = {
        funcService(FuncImpl) {
            
        }
    }
   
}
