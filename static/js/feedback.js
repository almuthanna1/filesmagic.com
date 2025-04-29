const form = document.getElementById('feedback-form');
const status = document.getElementById('status');

// Initialize Supabase client
const supabaseClient = supabase.createClient(
  'https://obxawkpojgoazkzmxbic.supabase.co',
  'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9ieGF3a3BvamdvYXprem14YmljIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDU3MDU4OTYsImV4cCI6MjA2MTI4MTg5Nn0.Q2QpKRLTXo164lazGKD4u6v-yC2xDrSb2gqqoxcdgLk'
);

form.addEventListener('submit', async function(event) {
    event.preventDefault(); // Stop the form from refreshing the page

    // Set "Submitting..." status
    status.textContent = 'Submitting feedback...';
    status.style.color = 'orange';

    // Grab the form field values
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const feedbackText = document.getElementById('feedback').value.trim();

    if (!feedbackText) {
        status.textContent = 'Feedback cannot be empty.';
        status.style.color = 'red';
        return; // Simply won't submit if the feedback box is empty
    }

    const { data, error } = await supabaseClient
      .from('feedback') // Table name goes here
      .insert([{ name, email, feedback: feedbackText }]);

    if (error) {
        console.error('Error submitting feedback:', error);
        status.textContent = 'Failed to submit feedback. Please try again.';
        status.style.color = 'red';
    } else {
        console.log('Feedback submitted successfully:', data);
        status.textContent = 'Thank you for your feedback!';
        status.style.color = 'green';
        form.reset(); // Reset the form ONLY after successful insert
    }
});
