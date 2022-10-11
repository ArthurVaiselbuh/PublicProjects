using System;
using System.Diagnostics;

namespace TaskKill
{
	public class Program
	{
		public static void Main(string[] args)
		{
			var pid = int.Parse(args[0]);
			KillTest(pid);
		}


		public static void KillTest(int pid)
		{
			var process = Process.GetProcessById(pid);
			Console.WriteLine($"Killing pid {pid}, named: {process.ProcessName}");
			process.Kill();
		}

	}
}
