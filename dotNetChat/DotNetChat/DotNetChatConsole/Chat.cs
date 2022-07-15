using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Net.Sockets;
using log4net;
using System.Net;

namespace DotNetChatConsole
{
    internal class ChatMessage
    {
        private int messageSize;
        private byte[]? message = null;

        public byte[] MessageBytes {get=> message!; }

        private ChatMessage() {}

        public byte[] ToBytes()
        {
            using var memoryStream = new MemoryStream();
            memoryStream.Write(BitConverter.GetBytes(IPAddress.HostToNetworkOrder(messageSize)));
            memoryStream.Write(message);
            return memoryStream.ToArray();
           
        }

        public static ChatMessage FromBytes(byte[] bytes)
        {
            ChatMessage result = new ChatMessage();
            result.messageSize = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(bytes));
            var size = result.messageSize - sizeof(int);
            result.message = new byte[size];
            Array.Copy(bytes, sizeof(int), result.message, 0, size);
            return result;
        }
        
        public static ChatMessage GetMessageFromString(string message)
        {
            var encodedMessage = Encoding.UTF8.GetBytes(message);
            ChatMessage chatMessage =new ChatMessage { message = encodedMessage, messageSize = encodedMessage.Length + sizeof(int) };
            return chatMessage; 
        }
    }

    internal class Chat
    {
        private static log4net.ILog log = log4net.LogManager.GetLogger(nameof(Chat));
        private Socket socket;
        public Chat(Socket socket)
        {
            this.socket = socket;
        }

        public async Task SendChatMessage(string message)
        {
            var encodedMessage = Encoding.UTF8.GetBytes(message);
            log.Debug($"Sending message: <{message}>, encoded length: {encodedMessage.Length}, encoded is: {encodedMessage}");
            var chatMessage = ChatMessage.GetMessageFromString(message);
            var bytesSent = await socket.SendAsync(chatMessage.ToBytes(), SocketFlags.None);
        }

        public async Task<string> ReadChatMessage()
        {
            log.Debug("Waiting on message from socket");
            var bytes = await ReadFullMessageFromSocket();
            log.Debug("Read full message");
            var chatMessage = ChatMessage.FromBytes(bytes);
            var decodedMessage = Encoding.UTF8.GetString(chatMessage.MessageBytes);
            log.Debug($"Received decoded message: {decodedMessage}");
            return decodedMessage;
        }

        private async Task<byte[]> ReadFullMessageFromSocket()
        {
            var bytes = new byte[1024];
            var recvSize = await socket.ReceiveAsync(bytes, SocketFlags.None);
            var size = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(bytes));
            if (size != recvSize)
            {
                throw new NotImplementedException("Not handling long messages for now");
            }
            return bytes;
        }


    }
}
