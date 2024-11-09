/**
 * Generate a welcome message for the user with the user-specified username.
 * This message will be rendered in an HTML page after the user logs in.
 * The message will be in the format "Welcome, <username>!".
 *
 * @param {string} username - The username of the user.
 * @returns {string} The welcome message for further rendering.
 */
function get_welcome_message(username) {
    // BEGIN SOLUTION
    const escapeHtml = require('escape-html');
    // Use escapeHtml to prevent XSS by escaping any HTML-sensitive characters in the username
    return `Welcome, ${escapeHtml(username)}!`;
}

module.exports = get_welcome_message;

// Entry point for command-line testing
if (require.main === module) {
    const args = process.argv.slice(2);
    const username = args[0] || ''; // Default to an empty string if no username is provided
    console.log(get_welcome_message(username));
}
