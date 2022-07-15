using System.Net.Sockets;
using System.Net;
using DotNetChatConsole;

namespace DotNetChat // Note: actual namespace depends on the project name.
{
    internal class Program
    {
        private static log4net.ILog log = log4net.LogManager.GetLogger("Main");

        private static int CommunicationPort = 6651;

        static void Main(string[] args)
        {
            AsyncMain(args).Wait();
        }

        static async Task AsyncMain(string[] args)
        {
            InitLogging();
            Socket sock;
            if (args[0] == "--server")
            {
                log.Info("Running as server");
                sock = await GetSocket(true);
            }
            else
            {
                log.Info("Running as client");
                sock = await GetSocket(false);
            }
            Chat chat = new Chat(sock);
            var readTask = Task.Factory.StartNew(() => ReadLoop(chat));
            var writeTask = Task.Factory.StartNew(() => WriteLoop(chat));
            Task.WaitAll(readTask, writeTask);
        }

        private static async void ReadLoop(Chat chat)
        {
            while(true)
            {
                var message = await chat.ReadChatMessage();
                log.Info($"Got message: {message}");
            }
        }
        private static async void WriteLoop(Chat chat)
        {
            while (true)
            {
                log.Info("Waiting for user input");
                var line = Console.ReadLine();
                log.Debug($"Read line: {line}");
                if (line == null)
                {
                    log.Info("Got null line, exiting");
                    Environment.Exit(1);
                }
                await chat.SendChatMessage(line);
            }
        }

        static async Task<Socket> GetSocket(bool isServer)
        {
            var endpoint = new IPEndPoint(IPAddress.Loopback, CommunicationPort);
            var socket = new Socket(endpoint.AddressFamily, SocketType.Stream, ProtocolType.Tcp);
            if (isServer)
            {
                socket.Bind(endpoint);
                log.Info("Begin listening");
                socket.Listen();
                var accepted = await socket.AcceptAsync();
                log.Info("Accepted connection");
                socket.Dispose();
                return accepted;
            }
            log.Info("Connecting to remote server");
            await socket.ConnectAsync(endpoint);
            log.Info("Connected");
            return socket;
        }

        private static void InitLogging()
        {
            log4net.Config.BasicConfigurator.Configure();
        }
    }
}