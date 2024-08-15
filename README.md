# Compere

Compere is an advanced comparative rating system that leverages Multi-Armed Bandit (MAB) algorithms and Elo ratings to provide fair and efficient entity comparisons. It's designed to improve decision-making processes by facilitating pairwise comparisons of entities such as restaurants, hotels, or any other items that benefit from relative ranking.

## Features

- **Multi-Armed Bandit (MAB) Algorithm**: Utilizes the Upper Confidence Bound (UCB) algorithm to balance exploration and exploitation in entity selection.
- **Elo Rating System**: Implements Elo ratings for accurate and dynamic entity ranking.
- **Cold-Start Problem Handling**: Prioritizes new entities to quickly integrate them into the comparison pool.
- **Asynchronous Processing**: Uses background tasks for efficient MAB state updates.
- **Modular Architecture**: Well-organized codebase with separate modules for different functionalities.
- **RESTful API**: Provides a comprehensive API for entity management, comparisons, and system monitoring.
- **User Authentication**: Implements JWT-based authentication for secure access.
- **Rate Limiting**: Protects the system from abuse with configurable rate limiting.
- **Monitoring and Logging**: Includes endpoints for system statistics and MAB performance metrics.

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy ORM (compatible with various SQL databases)
- **Authentication**: JWT (JSON Web Tokens)
- **Task Scheduling**: FastAPI built-in background tasks and repeat_every decorator

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/compere.git
   cd compere
   ```

2. Set up a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add the following:
   ```
   DATABASE_URL=sqlite:///./compere.db
   SECRET_KEY=your_secret_key_here
   ```

5. Initialize the database:
   ```
   python -m modules.database
   ```

6. Run the application:
   ```
   uvicorn main:app --reload
   ```

The API will be available at `http://localhost:8000`.

## Usage

### API Endpoints

- `/entities/`: CRUD operations for entities
- `/comparisons/`: Create and retrieve comparisons
- `/comparisons/next`: Get the next pair of entities to compare
- `/mab/update`: Update MAB state after a comparison
- `/mab/reset`: Reset MAB state (admin only)
- `/monitoring/system_stats`: Get system statistics
- `/monitoring/mab_stats`: Get MAB-specific statistics

For a complete list of endpoints and their usage, visit the Swagger UI at `http://localhost:8000/docs` when the application is running.

### Making a Comparison

1. Get the next pair of entities to compare:
   ```
   GET /comparisons/next
   ```

2. Submit a comparison:
   ```
   POST /comparisons/
   {
     "user_id": 1,
     "entity1_id": 5,
     "entity2_id": 8,
     "selected_entity_id": 5
   }
   ```

3. The system will automatically update the MAB state and Elo ratings based on the comparison.

## Contributing

Contributions to Compere are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch: `git checkout -b feature-branch-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-branch-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- The Elo rating system, developed by Arpad Elo
- The Multi-Armed Bandit algorithm and its applications in decision making
- The FastAPI framework and its community

For any questions or support, please open an issue in the GitHub repository.