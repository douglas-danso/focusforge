import React, { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Play, 
  Pause, 
  SkipForward, 
  SkipBack, 
  Music, 
  Timer, 
  Heart, 
  Brain, 
  Zap, 
  Moon, 
  Sun,
  Plus,
  Trash2,
  Settings,
  CheckCircle,
  Clock,
  Star
} from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { useRitualStore } from '../stores/useRitualStore';
import { useUIStore } from '../stores/useUIStore';

interface RitualStep {
  id: string;
  type: 'environment' | 'breathing' | 'meditation' | 'spotify' | 'intention' | 'custom';
  title: string;
  description: string;
  duration: number;
  config: any;
}

interface RitualTemplate {
  id: string;
  name: string;
  description: string;
  steps: RitualStep[];
  category: string;
  estimatedDuration: number;
  difficulty: 'beginner' | 'intermediate' | 'advanced';
}

const Rituals: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'templates' | 'builder' | 'execution'>('templates');
  const [selectedRitual, setSelectedRitual] = useState<RitualTemplate | null>(null);
  const [isExecuting, setIsExecuting] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [showBuilder, setShowBuilder] = useState(false);
  const [newRitual, setNewRitual] = useState<Partial<RitualTemplate>>({
    name: '',
    description: '',
    steps: [],
    category: 'focus',
    estimatedDuration: 0,
    difficulty: 'beginner'
  });

  const { rituals, createRitual } = useRitualStore();
  const { addNotification } = useUIStore();

  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Pre-built ritual templates
  const ritualTemplates: RitualTemplate[] = [
    {
      id: 'deep-work',
      name: 'Deep Work',
      description: 'Prepare your mind and environment for intense focus sessions',
      category: 'focus',
      estimatedDuration: 15,
      difficulty: 'intermediate',
      steps: [
        {
          id: '1',
          type: 'environment',
          title: 'Environment Setup',
          description: 'Clear your workspace, adjust lighting, silence notifications',
          duration: 3,
          config: { actions: ['clear_desk', 'adjust_lighting', 'silence_phone'] }
        },
        {
          id: '2',
          type: 'breathing',
          title: 'Box Breathing',
          description: '4-4-4-4 breathing pattern to center your mind',
          duration: 2,
          config: { pattern: '4-4-4-4', cycles: 3 }
        },
        {
          id: '3',
          type: 'intention',
          title: 'Set Intention',
          description: 'Clearly state your focus goal for this session',
          duration: 1,
          config: { prompt: 'What will you accomplish in this focus session?' }
        },
        {
          id: '4',
          type: 'spotify',
          title: 'Focus Playlist',
          description: 'Start your curated focus music',
          duration: 1,
          config: { playlist: 'deep_focus_2024', autoplay: true }
        }
      ]
    },
    {
      id: 'energy-boost',
      name: 'Energy Boost',
      description: 'Quick ritual to increase energy and motivation',
      category: 'energy',
      estimatedDuration: 8,
      difficulty: 'beginner',
      steps: [
        {
          id: '1',
          type: 'breathing',
          title: 'Energizing Breath',
          description: 'Quick breathing exercise to boost energy',
          duration: 2,
          config: { pattern: 'quick_inhale', cycles: 5 }
        },
        {
          id: '2',
          type: 'custom',
          title: 'Power Pose',
          description: 'Stand in a confident pose for 2 minutes',
          duration: 2,
          config: { pose: 'superhero_pose', duration: 120 }
        },
        {
          id: '3',
          type: 'spotify',
          title: 'High Energy Music',
          description: 'Play upbeat, motivating music',
          duration: 2,
          config: { playlist: 'energy_boost', volume: 0.8 }
        }
      ]
    },
    {
      id: 'calm-centered',
      name: 'Calm & Centered',
      description: 'Find your center and reduce stress before important tasks',
      category: 'calm',
      estimatedDuration: 12,
      difficulty: 'beginner',
      steps: [
        {
          id: '1',
          type: 'breathing',
          title: '4-7-8 Breathing',
          description: 'Calming breathing pattern',
          duration: 3,
          config: { pattern: '4-7-8', cycles: 4 }
        },
        {
          id: '2',
          type: 'meditation',
          title: 'Mindfulness',
          description: 'Brief mindfulness meditation',
          duration: 5,
          config: { type: 'mindfulness', voice: 'calm_female' }
        },
        {
          id: '3',
          type: 'environment',
          title: 'Create Calm Space',
          description: 'Adjust environment for tranquility',
          duration: 2,
          config: { lighting: 'warm', noise: 'minimal' }
        }
      ]
    },
    {
      id: 'creative-flow',
      name: 'Creative Flow',
      description: 'Unlock creativity and innovative thinking',
      category: 'creativity',
      estimatedDuration: 18,
      difficulty: 'advanced',
      steps: [
        {
          id: '1',
          type: 'meditation',
          title: 'Open Awareness',
          description: 'Open awareness meditation to expand thinking',
          duration: 8,
          config: { type: 'open_awareness', background: 'nature_sounds' }
        },
        {
          id: '2',
          type: 'spotify',
          title: 'Creative Inspiration',
          description: 'Play music that sparks creativity',
          duration: 5,
          config: { playlist: 'creative_flow', shuffle: true }
        },
        {
          id: '3',
          type: 'custom',
          title: 'Free Association',
          description: 'Write down 20 random thoughts',
          duration: 3,
          config: { method: 'free_writing', count: 20 }
        }
      ]
    }
  ];

  const stepTypes = [
    { type: 'environment', label: 'Environment', icon: Settings, color: 'bg-blue-500' },
    { type: 'breathing', label: 'Breathing', icon: Heart, color: 'bg-green-500' },
    { type: 'meditation', label: 'Meditation', icon: Brain, color: 'bg-purple-500' },
    { type: 'spotify', label: 'Music', icon: Music, color: 'bg-green-600' },
    { type: 'intention', label: 'Intention', icon: Star, color: 'bg-yellow-500' },
    { type: 'custom', label: 'Custom', icon: Zap, color: 'bg-orange-500' }
  ];

  const startRitual = (ritual: RitualTemplate) => {
    setSelectedRitual(ritual);
    setCurrentStepIndex(0);
    setIsExecuting(true);
    setTimeRemaining(ritual.steps[0].duration * 60);
    setActiveTab('execution');
  };

  const nextStep = () => {
    if (selectedRitual && currentStepIndex < selectedRitual.steps.length - 1) {
      setCurrentStepIndex(currentStepIndex + 1);
      const nextStep = selectedRitual.steps[currentStepIndex + 1];
      setTimeRemaining(nextStep.duration * 60);
    } else {
      completeRitual();
    }
  };

  const previousStep = () => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex(currentStepIndex - 1);
      const prevStep = selectedRitual!.steps[currentStepIndex - 1];
      setTimeRemaining(prevStep.duration * 60);
    }
  };

  const completeRitual = () => {
    setIsExecuting(false);
    setSelectedRitual(null);
    setCurrentStepIndex(0);
    setTimeRemaining(0);
    addNotification({
      type: 'success',
      title: 'Ritual Completed',
      message: 'Ritual completed successfully!'
    });
    setActiveTab('templates');
  };

  const addStep = () => {
    const newStep: RitualStep = {
      id: Date.now().toString(),
      type: 'custom',
      title: 'New Step',
      description: 'Step description',
      duration: 5,
      config: {}
    };
    setNewRitual(prev => ({
      ...prev,
      steps: [...(prev.steps || []), newStep]
    }));
  };

  const removeStep = (stepId: string) => {
    setNewRitual(prev => ({
      ...prev,
      steps: (prev.steps || []).filter(step => step.id !== stepId)
    }));
  };

  const saveRitual = () => {
    if (newRitual.name && newRitual.steps && newRitual.steps.length > 0) {
      const ritual: RitualTemplate = {
        ...newRitual,
        id: Date.now().toString(),
        estimatedDuration: newRitual.steps?.reduce((acc, step) => acc + step.duration, 0) || 0
      } as RitualTemplate;
      
      createRitual(ritual);
      setNewRitual({ name: '', description: '', steps: [], category: 'focus', estimatedDuration: 0, difficulty: 'beginner' });
      setShowBuilder(false);
      addNotification({
        type: 'success',
        title: 'Ritual Created',
        message: 'Ritual created successfully!'
      });
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const renderStepContent = (step: RitualStep) => {
    switch (step.type) {
      case 'breathing':
        return (
          <div className="text-center">
            <div className="text-6xl mb-4">🫁</div>
            <div className="text-2xl font-semibold mb-2">{step.title}</div>
            <div className="text-gray-600 mb-4">{step.description}</div>
            <div className="text-4xl font-mono text-blue-600">{formatTime(timeRemaining)}</div>
          </div>
        );
      
      case 'meditation':
        return (
          <div className="text-center">
            <div className="text-6xl mb-4">🧘‍♀️</div>
            <div className="text-2xl font-semibold mb-2">{step.title}</div>
            <div className="text-gray-600 mb-4">{step.description}</div>
            <div className="text-4xl font-mono text-purple-600">{formatTime(timeRemaining)}</div>
          </div>
        );
      
      case 'spotify':
        return (
          <div className="text-center">
            <div className="text-6xl mb-4">🎵</div>
            <div className="text-2xl font-semibold mb-2">{step.title}</div>
            <div className="text-gray-600 mb-4">{step.description}</div>
            <div className="flex justify-center space-x-4 mt-6">
              <Button onClick={() => setIsPlaying(!isPlaying)} variant="outline" size="lg">
                {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
              </Button>
              <Button onClick={previousStep} variant="outline" size="lg">
                <SkipBack className="w-6 h-6" />
              </Button>
              <Button onClick={nextStep} variant="outline" size="lg">
                <SkipForward className="w-6 h-6" />
              </Button>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="text-center">
            <div className="text-6xl mb-4">✨</div>
            <div className="text-2xl font-semibold mb-2">{step.title}</div>
            <div className="text-gray-600 mb-4">{step.description}</div>
            <div className="text-4xl font-mono text-gray-600">{formatTime(timeRemaining)}</div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Rituals</h1>
          <p className="text-gray-600">Create and execute personalized productivity rituals</p>
        </motion.div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white rounded-2xl p-1 mb-8 shadow-sm">
          {[
            { id: 'templates', label: 'Templates', count: ritualTemplates.length },
            { id: 'builder', label: 'Builder', count: newRitual.steps?.length || 0 },
            { id: 'execution', label: 'Execution', count: isExecuting ? 1 : 0 }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 py-3 px-4 rounded-xl font-medium transition-all duration-200 ${
                activeTab === tab.id
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              {tab.label}
              {tab.count > 0 && (
                <span className="ml-2 bg-white/20 px-2 py-1 rounded-full text-xs">
                  {tab.count}
                </span>
              )}
            </button>
          ))}
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 'templates' && (
            <motion.div
              key="templates"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              {/* Template Categories */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                {['focus', 'energy', 'calm', 'creativity'].map((category) => (
                  <motion.div
                    key={category}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className="bg-white rounded-2xl p-4 text-center cursor-pointer shadow-sm hover:shadow-md transition-all"
                  >
                    <div className="text-2xl mb-2">
                      {category === 'focus' && <Brain className="w-8 h-8 mx-auto text-blue-600" />}
                      {category === 'energy' && <Zap className="w-8 h-8 mx-auto text-yellow-600" />}
                      {category === 'calm' && <Moon className="w-8 h-8 mx-auto text-purple-600" />}
                      {category === 'creativity' && <Star className="w-8 h-8 mx-auto text-orange-600" />}
                    </div>
                    <div className="font-semibold capitalize">{category}</div>
                  </motion.div>
                ))}
              </div>

              {/* Ritual Templates */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {ritualTemplates.map((ritual) => (
                  <motion.div
                    key={ritual.id}
                    whileHover={{ y: -4 }}
                    className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-lg transition-all cursor-pointer"
                    onClick={() => startRitual(ritual)}
                  >
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full ${
                          ritual.difficulty === 'beginner' ? 'bg-green-500' :
                          ritual.difficulty === 'intermediate' ? 'bg-yellow-500' : 'bg-red-500'
                        }`} />
                        <span className="text-sm text-gray-500 capitalize">{ritual.difficulty}</span>
                      </div>
                      <div className="flex items-center space-x-1 text-gray-400">
                        <Clock className="w-4 h-4" />
                        <span className="text-sm">{ritual.estimatedDuration}m</span>
                      </div>
                    </div>
                    
                    <h3 className="text-xl font-semibold mb-2">{ritual.name}</h3>
                    <p className="text-gray-600 mb-4">{ritual.description}</p>
                    
                    <div className="flex items-center justify-between">
                      <div className="flex space-x-1">
                        {ritual.steps.slice(0, 3).map((step, index) => (
                          <div
                            key={step.id}
                            className={`w-2 h-2 rounded-full ${
                              step.type === 'breathing' ? 'bg-green-500' :
                              step.type === 'meditation' ? 'bg-purple-500' :
                              step.type === 'spotify' ? 'bg-green-600' :
                              step.type === 'environment' ? 'bg-blue-500' :
                              step.type === 'intention' ? 'bg-yellow-500' : 'bg-orange-500'
                            }`}
                          />
                        ))}
                        {ritual.steps.length > 3 && (
                          <span className="text-xs text-gray-400">+{ritual.steps.length - 3}</span>
                        )}
                      </div>
                      <Button size="sm" onClick={(e) => { e.stopPropagation(); startRitual(ritual); }}>
                        <Play className="w-4 h-4 mr-2" />
                        Start
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* Create Custom Ritual Button */}
              <motion.div
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className="text-center"
              >
                <Button
                  size="lg"
                  onClick={() => setShowBuilder(true)}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                >
                  <Plus className="w-5 h-5 mr-2" />
                  Create Custom Ritual
                </Button>
              </motion.div>
            </motion.div>
          )}

          {activeTab === 'builder' && (
            <motion.div
              key="builder"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              <Card className="p-6">
                <h2 className="text-2xl font-semibold mb-6">Custom Ritual Builder</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Ritual Name</label>
                    <Input
                      value={newRitual.name}
                      onChange={(e) => setNewRitual(prev => ({ ...prev, name: e.target.value }))}
                      placeholder="e.g., Morning Power Ritual"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
                    <select
                      value={newRitual.category}
                      onChange={(e) => setNewRitual(prev => ({ ...prev, category: e.target.value }))}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="focus">Focus</option>
                      <option value="energy">Energy</option>
                      <option value="calm">Calm</option>
                      <option value="creativity">Creativity</option>
                      <option value="custom">Custom</option>
                    </select>
                  </div>
                </div>

                <div className="mb-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                  <textarea
                    value={newRitual.description}
                    onChange={(e) => setNewRitual(prev => ({ ...prev, description: e.target.value }))}
                    placeholder="Describe what this ritual helps you achieve..."
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent h-20 resize-none"
                  />
                </div>

                <div className="mb-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold">Ritual Steps</h3>
                    <Button onClick={addStep} size="sm">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Step
                    </Button>
                  </div>

                  <div className="space-y-4">
                    {newRitual.steps?.map((step, index) => (
                      <motion.div
                        key={step.id}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="bg-gray-50 rounded-lg p-4"
                      >
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Step Type</label>
                            <select
                              value={step.type}
                              onChange={(e) => {
                                const updatedSteps = [...(newRitual.steps || [])];
                                updatedSteps[index].type = e.target.value as any;
                                setNewRitual(prev => ({ ...prev, steps: updatedSteps }));
                              }}
                              className="w-full px-2 py-1 border border-gray-300 rounded focus:ring-1 focus:ring-blue-500"
                            >
                              {stepTypes.map(type => (
                                <option key={type.type} value={type.type}>{type.label}</option>
                              ))}
                            </select>
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
                            <Input
                              value={step.title}
                              onChange={(e) => {
                                const updatedSteps = [...(newRitual.steps || [])];
                                updatedSteps[index].title = e.target.value;
                                setNewRitual(prev => ({ ...prev, steps: updatedSteps }));
                              }}
                              placeholder="Step title"
                            />
                          </div>
                          <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Duration (min)</label>
                            <Input
                              type="number"
                              value={step.duration}
                              onChange={(e) => {
                                const updatedSteps = [...(newRitual.steps || [])];
                                updatedSteps[index].duration = parseInt(e.target.value) || 1;
                                setNewRitual(prev => ({ ...prev, steps: updatedSteps }));
                              }}
                              min="1"
                              max="60"
                            />
                          </div>
                          <div className="flex items-end">
                            <Button
                              onClick={() => removeStep(step.id)}
                              variant="outline"
                              size="sm"
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                        
                        <div className="mt-3">
                          <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                          <textarea
                            value={step.description}
                            onChange={(e) => {
                              const updatedSteps = [...(newRitual.steps || [])];
                              updatedSteps[index].description = e.target.value;
                              setNewRitual(prev => ({ ...prev, steps: updatedSteps }));
                            }}
                            placeholder="Describe what happens in this step..."
                            className="w-full px-2 py-1 border border-gray-300 rounded focus:ring-1 focus:ring-blue-500 h-16 resize-none"
                          />
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end space-x-4">
                  <Button variant="outline" onClick={() => setShowBuilder(false)}>
                    Cancel
                  </Button>
                  <Button onClick={saveRitual} disabled={!newRitual.name || !newRitual.steps || newRitual.steps.length === 0}>
                    Save Ritual
                  </Button>
                </div>
              </Card>
            </motion.div>
          )}

          {activeTab === 'execution' && selectedRitual && (
            <motion.div
              key="execution"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              className="space-y-6"
            >
              {/* Progress Bar */}
              <div className="bg-white rounded-2xl p-6 shadow-sm">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-2xl font-semibold">{selectedRitual.name}</h2>
                  <div className="text-sm text-gray-500">
                    Step {currentStepIndex + 1} of {selectedRitual.steps.length}
                  </div>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
                  <motion.div
                    className="bg-blue-600 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${((currentStepIndex + 1) / selectedRitual.steps.length) * 100}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              {/* Current Step */}
              <Card className="p-12 text-center">
                {renderStepContent(selectedRitual.steps[currentStepIndex])}
              </Card>

              {/* Navigation Controls */}
              <div className="flex justify-center space-x-4">
                <Button
                  onClick={previousStep}
                  disabled={currentStepIndex === 0}
                  variant="outline"
                  size="lg"
                >
                  <SkipBack className="w-5 h-5 mr-2" />
                  Previous
                </Button>
                
                <Button
                  onClick={nextStep}
                  size="lg"
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {currentStepIndex === selectedRitual.steps.length - 1 ? (
                    <>
                      <CheckCircle className="w-5 h-5 mr-2" />
                      Complete
                    </>
                  ) : (
                    <>
                      <SkipForward className="w-5 h-5 mr-2" />
                      Next
                    </>
                  )}
                </Button>
              </div>

              {/* Step Overview */}
              <div className="bg-white rounded-2xl p-6 shadow-sm">
                <h3 className="text-lg font-semibold mb-4">Ritual Overview</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {selectedRitual.steps.map((step, index) => (
                    <div
                      key={step.id}
                      className={`p-4 rounded-lg border-2 transition-all ${
                        index === currentStepIndex
                          ? 'border-blue-500 bg-blue-50'
                          : index < currentStepIndex
                          ? 'border-green-500 bg-green-50'
                          : 'border-gray-200 bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-white text-sm font-semibold ${
                          index === currentStepIndex
                            ? 'bg-blue-500'
                            : index < currentStepIndex
                            ? 'bg-green-500'
                            : 'bg-gray-400'
                        }`}>
                          {index < currentStepIndex ? '✓' : index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium">{step.title}</div>
                          <div className="text-sm text-gray-500">{step.duration}m</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

export default Rituals;
