import functions_framework
import earn
import lend
import vaults_ethereum


@functions_framework.http
def trigger(request):
    lend.trigger_lend()
    earn.trigger_earn()
    vaults_ethereum.trigger()
    return 'Done'
