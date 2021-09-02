#if defined(_WIN32)
#ifndef _WIN32_WINNT
#define _WIN32_WINNT 0x0600
#endif
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "ws2_32.lib")

#else
#include<sys/types.h>
#include<sys/socket.h>
#include<netinet/in.h>
#include<arpa/inet.h>
#include<netdb.h>
#include<unistd.h>
#include<errno.h>
#endif

#if defined(_WIN32)
#define ISVALIDSOCKET(s) ((s) != INVALID_SOCKET)
#define CLOSESOCKET(s) closesocket(s)
#define GETSOCKETERRNO() (WSAGetLastError())
#else
#define ISVALIDSOCKET(s) ((s) >= 0)
#define CLOSESOCKET(s) close(s)
#define SOCKET int
#define GETSOCKETERRNO() (errno)
#endif

#include <stdio.h>
#include <string.h>
#include <time.h>

#if defined(_WIN32)
#include <conio.h>
#endif


int main(int argc, char *argv[]) {
    #if defined(_WIN32)
        WSADATA d;
        if (WSAStartup(MAKEWORD(2, 2), &d)) {
            fprintf(stderr, "Failed to initialize.\n");
            return 1;
        }
    #endif

    if (argc < 3) {
        fprintf(stderr, "usage: tcp_client hostname port\n");
        return 1;
    }

    printf("Configuring remote address...\n");
    struct addrinfo hints;
    memset(&hints, 0, sizeof(hints));
    hints.ai_socktype = SOCK_STREAM;
    struct addrinfo *peer_address;
    if (getaddrinfo(argv[1], argv[2], &hints, &peer_address)) {
        fprintf(stderr, "getaddrinfo() failed. (%d)\n", GETSOCKETERRNO());
        return 1;
    }

    printf("Remote address is: ");
    char address_buffer[100];
    char service_buffer[100];
    getnameinfo(peer_address->ai_addr, peer_address->ai_addrlen, address_buffer, sizeof(address_buffer), service_buffer, sizeof(service_buffer), NI_NUMERICHOST);
    printf("%s %s\n", address_buffer, service_buffer);

    printf("Creating socket...\n");
    SOCKET socket_peer;
    socket_peer = socket(peer_address->ai_family, peer_address->ai_socktype, peer_address->ai_protocol);
    if (!ISVALIDSOCKET(socket_peer)) {
        fprintf(stderr, "socket() failed. (%d)\n", GETSOCKETERRNO());
        return 1;
    }

    printf("Connecting...\n");
    if (connect(socket_peer, peer_address->ai_addr, peer_address->ai_addrlen)) {
        fprintf(stderr, "connect() failed. (%d)\n", GETSOCKETERRNO());
        return 1;
    }
    freeaddrinfo(peer_address);

    printf("Connected.\n");
    printf("To send data, enter text followed by enter.\n");

    while(1){
        fd_set reads;
        FD_ZERO(&reads);
        FD_SET(socket_peer, &reads);
        #if !defined(_WIN32)
            FD_SET(0, &reads);  //on non-windows, add "stdin" to the "reads" set. This works because 0 is the file descriptor for stdin.
                                //Alternatively, we could have used FD_SET(fileno(stdin), &reads) to the same effect.

        #endif
        struct timeval timeout;
        timeout.tv_sec = 0;
        timeout.tv_usec = 100000;
        if (select(socket_peer+1, &reads, 0, 0, &timeout) < 0){
            fprintf(stderr, "select() failed. (%d)\n", GETSOCKETERRNO());
            return 1;
        }

        if (FD_ISSET(socket_peer, &reads)) {
            char read[4096];
            int bytes_received = recv(socket_peer, read, 4096, 0);
            if (bytes_received < 1) {
                printf("Connection closed by peer.\n");
                break;
            }
            printf("Received (%d bytes): %.*s", bytes_received, bytes_received, read);
        }

        #if defined(_WIN32)
            if(_kbhit()){
        #else
            if(FD_ISSET(0, &reads)) {
        #endif
        char read[4096];
        if (!fgets(read, 4096, stdin)) 
            break;
        printf("Sending: %s", read); 
        int bytes_sent = send(socket_peer, read, strlen(read), 0);
        printf("Sent %d bytes.\n", bytes_sent);
        }
        /*
            On Windows, we use the _kbhit() function to indicate whether any console input is
        waiting. _kbhit() returns non-zero if an unhandled key press event is queued up. For
        Unix-based systems, we simply check if select() sets the stdin file descriptor, 0. If input
        is ready, we call fgets() to read the next line of input. This input is then sent over our
        connected socket with send().
        */

        /*
        This select() based terminal monitoring works very well on Unix-based systems. It also
        works equally well if input is piped in. For example, you could use our TCP client program
        to send a text file with a command such as cat my_file.txt | tcp_client
        192.168.54.122 8080.
        */

        /*
        The Windows terminal handling leaves a bit to be desired. Windows does not provide an
        easy way to tell whether stdin has input available without blocking, so we use _kbhit()
        as a poor proxy. However, if the user presses a non-printable key, such as an arrow key, it
        still triggers _kbhit(), even though there is no character to read. Also, after the first key
        press, our program will block on fgets() until the user presses the Enter key. (This doesn't
        happen on shells that buffer entire lines, which is common outside of Windows.) This
        blocking behavior is acceptable, but you should know that any received TCP data will not
        display until after that point. _kbhit() does not work for piped input. Doing proper piped
        and console input on Windows is possible, of course, but it's very complicated.
        We would need to use separate functions for each (PeekNamedPipe() and
        PeekConsoleInput()), and the logic for handling it would be as long as this entire
        program! Since handling terminal input isn't the purpose of this book, we're going to accept
        _kbhit() function's limitations and move on.
        */

    }
    printf("Closing socket...\n");
    CLOSESOCKET(socket_peer);

    #if defined(_WIN32)
        WSACleanup();
    #endif

printf("Finished.\n");
return 0;

}