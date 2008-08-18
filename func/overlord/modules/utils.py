import time

from func.overlord import overlord_module
import func.jobthing as jobthing

class utils(overlord_module.BaseModule):
    def __diff_dicts(self, a, b):
        return dict([(k, v) for k, v in a.iteritems() if k not in b])
        

    def async_poll(self, job_id, partial_func=None, interval=0.5):
        async_done = False
        partial = {}
        while not async_done:
            (return_code, async_results) = self.parent.job_status(job_id)
            if return_code == jobthing.JOB_ID_RUNNING:
                pass
            elif return_code == jobthing.JOB_ID_FINISHED:
                async_done = True
                if partial_func:
                    diff = self.__diff_dicts(async_results, partial)
                    if len(diff) > 0:
                        partial_func(diff)
                return async_results
            elif return_code == jobthing.JOB_ID_PARTIAL:
                pass
                if partial_func:
                    diff = self.__diff_dicts(async_results, partial)
                    if len(diff) > 0:
                        partial_func(diff)
                        partial=async_results
            else:
                #FIXME -- raise exception instead of printing
                print "Async error", return_code, async_results
                return 0

            time.sleep(interval)

    def list_minions(self):
       return self.parent.minions
