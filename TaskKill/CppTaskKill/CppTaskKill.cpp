#include <iostream>
#include <string>
#include <windows.h>

using namespace std;

void killProcess(int pid)
{
    auto process_handle = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION | PROCESS_TERMINATE, false, pid);
    if (process_handle == INVALID_HANDLE_VALUE || process_handle == 0)
    {
        cout << "OpenProcess failed with error: " << GetLastError() << endl;
        return;
    }

    auto result = TerminateProcess(process_handle, 1);
    if (result == 0)
    {
        cout << "Failed to terminate process " << pid << " with eror: " << GetLastError() << endl;
        return;
    }
    cout << "Successfully killed " << pid << endl;

    if (process_handle != INVALID_HANDLE_VALUE)
    {
        CloseHandle(process_handle);
    }
}

int main(int argc, char* argv[])
{
    if (argc != 2)
    {
        cout << "Invalid number of arguments" << endl;
        return 1;
    }

    cout << "Will attempt killing pid" << argv[1] << endl;
    auto pid = stoi(argv[1]);
    killProcess(pid);
    getc(stdin);
}
