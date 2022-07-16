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
        private static log4net.ILog log = log4net.LogManager.GetLogger(nameof(ChatMessage));

        private int contentSize;
        private byte[]? message = null;

        public byte[] MessageBytes {get=> message!; }

        private ChatMessage() {}

        public byte[] ToBytes()
        {
            using var memoryStream = new MemoryStream();
            memoryStream.Write(BitConverter.GetBytes(IPAddress.HostToNetworkOrder(contentSize)));
            memoryStream.Write(message);
            return memoryStream.ToArray();
           
        }

        public static ChatMessage FromBytes(byte[] bytes)
        {
            ChatMessage result = new ChatMessage();
            var contentSize = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(bytes));
            //log.Debug($"Attempting to construct message with content size: {contentSize}");
            result.contentSize = contentSize;
            result.message = new byte[contentSize];
            Array.Copy(bytes, sizeof(int), result.message, 0, contentSize);
            return result;
        }
        
        public static ChatMessage GetMessageFromString(string message)
        {
            var encodedMessage = Encoding.UTF8.GetBytes(message);
            ChatMessage chatMessage =new ChatMessage { message = encodedMessage, contentSize = encodedMessage.Length };
            return chatMessage; 
        }
    }

    internal class Chat
    {
        private static log4net.ILog log = log4net.LogManager.GetLogger(nameof(Chat));
        private NetworkStream connectionStream;
        public Chat(NetworkStream stream)
        {
            this.connectionStream = stream;
        }

        public async Task SendChatMessage(string message)
        {
            var encodedMessage = Encoding.UTF8.GetBytes(message);
            log.Debug($"Sending message: <{message}>, encoded length: {encodedMessage.Length}");
            var chatMessage = ChatMessage.GetMessageFromString(message);
            var bytesToSend = chatMessage.ToBytes();
            await connectionStream.WriteAsync(bytesToSend, 0, bytesToSend.Length);
        }

        public async Task<string> ReadChatMessage()
        {
            log.Debug("Waiting on message from socket");
            var bytes = await ReadFullMessageFromSocket();
            log.Debug("Finished reading full message");
            var chatMessage = ChatMessage.FromBytes(bytes);
            var decodedMessage = Encoding.UTF8.GetString(chatMessage.MessageBytes);
            log.Debug($"Received decoded message: {decodedMessage}");
            return decodedMessage;
        }

        private async Task<byte[]> ReadFullMessageFromSocket()
        {
            var bytes = new byte[1024];
            await connectionStream.ReadAsync(bytes, 0, sizeof(int));
            var contentSize = IPAddress.NetworkToHostOrder(BitConverter.ToInt32(bytes));
            if (contentSize > bytes.Length)
            {
                var newBytes = new byte[contentSize];
                Array.Copy(bytes, 0, destinationArray: newBytes, 0, sizeof(int));
                bytes = newBytes;
            }

            await connectionStream.ReadAsync(bytes, sizeof(int), contentSize);
            return bytes;
        }


    }
}
