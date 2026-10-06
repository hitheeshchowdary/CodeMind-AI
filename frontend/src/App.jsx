import { useRef, useState } from 'react'
import './App.css'
import RepositoryWorkspace from './components/RepositoryWorkspace'

const API_BASE_URL = 'http://localhost:8000'

const PROJECTS_STORAGE_KEY =
  'codemind_projects'

const ACTIVE_PROJECT_KEY =
  'codemind_active_project'

function App() {
  const fileInputRef = useRef(null)

  const [selectedFile, setSelectedFile] =
    useState(null)

  const [isDragging, setIsDragging] =
    useState(false)

  const [isUploading, setIsUploading] =
    useState(false)

  const [error, setError] =
    useState('')

  /*
   * Load all saved projects.
   */
  const [projects, setProjects] = useState(() => {
    try {
      const savedProjects =
        localStorage.getItem(
          PROJECTS_STORAGE_KEY,
        )

      if (!savedProjects) {
        return []
      }

      const parsedProjects =
        JSON.parse(savedProjects)

      if (!Array.isArray(parsedProjects)) {
        return []
      }

      /*
       * Remove any old duplicates that may
       * already exist in localStorage.
       */
      const uniqueProjects = []

      parsedProjects.forEach((project) => {
        if (!project?.repository_name) {
          return
        }

        const existingIndex =
          uniqueProjects.findIndex(
            (existingProject) =>
              existingProject.repository_name ===
              project.repository_name,
          )

        if (existingIndex === -1) {
          uniqueProjects.push(project)
        } else {
          /*
           * Keep the latest version.
           */
          uniqueProjects[existingIndex] =
            project
        }
      })

      return uniqueProjects
    } catch (storageError) {
      console.error(
        'Unable to load projects:',
        storageError,
      )

      return []
    }
  })

  /*
   * Load the currently active project.
   */
  const [activeProject, setActiveProject] =
    useState(() => {
      try {
        const savedActiveProject =
          localStorage.getItem(
            ACTIVE_PROJECT_KEY,
          )

        return savedActiveProject
          ? JSON.parse(savedActiveProject)
          : null
      } catch (storageError) {
        console.error(
          'Unable to load active project:',
          storageError,
        )

        return null
      }
    })

  /*
   * Save projects whenever the list changes.
   */
  const saveProjects = (updatedProjects) => {
    setProjects(updatedProjects)

    try {
      localStorage.setItem(
        PROJECTS_STORAGE_KEY,
        JSON.stringify(updatedProjects),
      )
    } catch (storageError) {
      console.error(
        'Unable to save projects:',
        storageError,
      )
    }
  }

  /*
   * Save the active project.
   */
  const setCurrentProject = (project) => {
    setActiveProject(project)

    try {
      if (project) {
        localStorage.setItem(
          ACTIVE_PROJECT_KEY,
          JSON.stringify(project),
        )
      } else {
        localStorage.removeItem(
          ACTIVE_PROJECT_KEY,
        )
      }
    } catch (storageError) {
      console.error(
        'Unable to save active project:',
        storageError,
      )
    }
  }

  const handleFileSelect = (file) => {
    setError('')

    if (!file) {
      return
    }

    if (!file.name.toLowerCase().endsWith('.zip')) {
      setSelectedFile(null)

      setError(
        'Please select a ZIP file containing your repository.',
      )

      return
    }

    setSelectedFile(file)
  }

  const handleInputChange = (event) => {
    const file =
      event.target.files?.[0]

    handleFileSelect(file)
  }

  const handleDrop = (event) => {
    event.preventDefault()

    setIsDragging(false)

    const file =
      event.dataTransfer.files?.[0]

    handleFileSelect(file)
  }

  const handleDragOver = (event) => {
    event.preventDefault()

    setIsDragging(true)
  }

  const handleDragLeave = (event) => {
    event.preventDefault()

    setIsDragging(false)
  }

  const openFilePicker = () => {
    fileInputRef.current?.click()
  }

  const resetUpload = () => {
    setSelectedFile(null)
    setError('')

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  /*
   * Upload repository.
   */
  const uploadRepository = async () => {
    if (!selectedFile || isUploading) {
      return
    }

    setIsUploading(true)
    setError('')

    try {
      const formData = new FormData()

      formData.append(
        'file',
        selectedFile,
      )

      const response = await fetch(
        `${API_BASE_URL}/repository/upload`,
        {
          method: 'POST',
          body: formData,
        },
      )

      const data =
        await response.json()

      if (!response.ok) {
        throw new Error(
          data?.detail ||
            'Repository upload failed. Please try again.',
        )
      }

      /*
       * IMPORTANT:
       *
       * Instead of simply adding the repository,
       * check whether it already exists.
       *
       * If it exists, replace it.
       * This prevents duplicates.
       */
      const existingProjectIndex =
        projects.findIndex(
          (project) =>
            project.repository_name ===
            data.repository_name,
        )

      let updatedProjects

      if (existingProjectIndex !== -1) {
        updatedProjects =
          projects.map((project) =>
            project.repository_name ===
            data.repository_name
              ? data
              : project,
          )
      } else {
        updatedProjects = [
          data,
          ...projects,
        ]
      }

      saveProjects(updatedProjects)

      /*
       * Open the uploaded project.
       */
      setCurrentProject(data)

      setSelectedFile(null)

      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    } catch (uploadError) {
      console.error(
        'Repository upload error:',
        uploadError,
      )

      setError(
        uploadError.message ||
          'Unable to connect to the CodeMind AI backend.',
      )
    } finally {
      setIsUploading(false)
    }
  }

  /*
   * Opens the upload page but DOES NOT
   * delete existing projects.
   */
  const handleNewProject = () => {
    setSelectedFile(null)
    setError('')
    setCurrentProject(null)

    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
  }

  /*
   * Select a previous project.
   */
  const handleSelectProject = (project) => {
    if (!project) {
      return
    }

    setError('')
    setSelectedFile(null)

    setCurrentProject(project)
  }

  /*
   * Remove a project completely.
   */
  const handleRemoveProject = (
    repositoryName,
  ) => {
    const shouldRemove =
      window.confirm(
        `Remove "${repositoryName}" from your project history?`,
      )

    if (!shouldRemove) {
      return
    }

    const updatedProjects =
      projects.filter(
        (project) =>
          project.repository_name !==
          repositoryName,
      )

    saveProjects(updatedProjects)

    if (
      activeProject?.repository_name ===
      repositoryName
    ) {
      setCurrentProject(null)
    }
  }

  /*
   * If there is an active project,
   * show the workspace.
   */
  if (activeProject) {
    return (
      <RepositoryWorkspace
        repository={activeProject}
        projects={projects}
        onSelectProject={
          handleSelectProject
        }
        onNewProject={
          handleNewProject
        }
        onRemoveProject={
          handleRemoveProject
        }
      />
    )
  }

  /*
   * Upload page.
   */
  return (
    <div className="app-shell">
      <header className="navbar">
        <div className="brand">
          <div className="brand-mark">
            <span>&lt;/&gt;</span>
          </div>

          <span className="brand-name">
            CodeMind
          </span>

          <span className="brand-ai">
            AI
          </span>
        </div>

        <nav className="nav-links">
          <a href="#how-it-works">
            How it works
          </a>

          <a href="#github">
            GitHub
          </a>
        </nav>
      </header>

      <main className="hero-section">
        <div className="hero-content">
          <div className="status-badge">
            <span className="status-dot" />

            AI-powered repository assistant
          </div>

          <h1>
            Understand your
            <span className="gradient-text">
              {' '}
              codebase
              {' '}
            </span>
            with AI.
          </h1>

          <p className="hero-description">
            Upload your repository and ask
            questions about your code.
            CodeMind AI understands your
            project, finds relevant files,
            and gives you clear,
            context-aware answers.
          </p>

          <div
            className={`upload-card ${
              isDragging
                ? 'upload-card-dragging'
                : ''
            }`}
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
          >
            <div className="upload-icon">
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.7"
                aria-hidden="true"
              >
                <path
                  d="M12 16V4m0 0L7.5 8.5M12 4l4.5 4.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />

                <path
                  d="M5 14v4.5A1.5 1.5 0 0 0 6.5 20h11a1.5 1.5 0 0 0 1.5-1.5V14"
                  strokeLinecap="round"
                />
              </svg>
            </div>

            <h2>
              {isDragging
                ? 'Drop your repository here'
                : 'Upload your repository'}
            </h2>

            <p>
              Drag and drop a{' '}
              <strong>.zip</strong> file here
              <br />
              or browse your computer
            </p>

            <input
              ref={fileInputRef}
              type="file"
              accept=".zip,application/zip"
              onChange={handleInputChange}
              hidden
            />

            {selectedFile && (
              <div className="selected-file">
                <div className="file-info">
                  <span className="file-icon">
                    ZIP
                  </span>

                  <div className="file-details">
                    <span className="file-name">
                      {selectedFile.name}
                    </span>

                    <span className="file-size">
                      {(
                        selectedFile.size /
                        (1024 * 1024)
                      ).toFixed(2)}{' '}
                      MB
                    </span>
                  </div>
                </div>

                <button
                  className="remove-file-button"
                  type="button"
                  onClick={resetUpload}
                  disabled={isUploading}
                >
                  ×
                </button>
              </div>
            )}

            {!selectedFile ? (
              <button
                className="browse-button"
                type="button"
                onClick={openFilePicker}
              >
                Browse files
              </button>
            ) : (
              <button
                className="browse-button upload-button"
                type="button"
                onClick={
                  uploadRepository
                }
                disabled={isUploading}
              >
                {isUploading ? (
                  <>
                    <span className="spinner" />
                    Indexing repository...
                  </>
                ) : (
                  'Upload repository'
                )}
              </button>
            )}

            {error ? (
              <div className="error-message">
                <span>!</span>
                {' '}
                {error}
              </div>
            ) : (
              <span className="upload-hint">
                ZIP files containing your
                source code
              </span>
            )}
          </div>
        </div>
      </main>

      <footer className="footer">
        <span>CodeMind AI</span>

        <span>
          Understand. Explore. Build.
        </span>
      </footer>
    </div>
  )
}

export default App