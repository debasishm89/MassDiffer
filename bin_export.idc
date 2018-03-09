#include <idc.idc>
static main()
{
    Batch(0);
    Wait();
    RunPlugin("zynamics_binexport_8", 2 );
	Exit(0);
}