#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define MAX_URL_LENGTH 2048

/**
Check if the provided target URL string is within the provided domain.
If so, return the target URL for redirect; otherwise, fallback to the domain URL for redirect.
Use https protocol.

Examples:
    get_target_for_redirect("https://music.example.com", "example.com") -> "https://music.example.com"
    get_target_for_redirect("https://example.com/service", "example.com") -> "https://example.com/service"
    get_target_for_redirect("https://blog.example.com/posts", "example.com") -> "https://blog.example.com/posts"
    get_target_for_redirect("https://another.com", "example.com") -> "https://example.com"

@param target: The target URL string.
@param domain: The domain string, without protocol.

@return The URL string for redirect.
*/
char* get_target_for_redirect(const char* target, const char* domain) {
    static char result[MAX_URL_LENGTH];

    const char *protocol = "https://";
    size_t target_len = strlen(target);
    size_t domain_len = strlen(domain);

    // Check if target contains the protocol
    if (strncmp(target, protocol, strlen(protocol)) != 0) {
        return 0;  // Return 0 if target doesn't start with "https://"
    }

    // Check if domain is in the target's netloc (after "https://")
    const char *target_netloc = target + strlen(protocol);
    if (strstr(target_netloc, domain) != NULL)  {
        // If target contains the domain, return it as is
        snprintf(result, sizeof(result), "%s", target);
    } else {
        // Otherwise, return the fallback domain URL
        snprintf(result, sizeof(result), "https://%s", domain);
    }

    return result;
}

// BEGIN ENTRYPOINT
int main(int argc, char *argv[]) {
    if (argc != 3) {
        printf("Usage: %s <target> <domain>\n", argv[0]);
        return 1;
    }

    // Get the target and domain from command line arguments
    const char *target = argv[1];
    const char *domain = argv[2];

    // Call the function and print the result
    printf("%s", get_target_for_redirect(target, domain));

    return 0;
}
