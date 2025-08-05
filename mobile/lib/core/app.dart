import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';
import '../features/dashboard/presentation/bloc/dashboard_bloc.dart';
import '../features/tasks/presentation/bloc/tasks_bloc.dart';
import '../features/pomodoro/presentation/bloc/pomodoro_bloc.dart';
import '../features/analytics/presentation/bloc/analytics_bloc.dart';
import '../features/store/presentation/bloc/store_bloc.dart';
import 'router/app_router.dart';
import 'theme/app_theme.dart';
import 'di/injection_container.dart' as di;

class FocusForgeApp extends StatelessWidget {
  const FocusForgeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiBlocProvider(
      providers: [
        BlocProvider(create: (_) => di.sl<DashboardBloc>()),
        BlocProvider(create: (_) => di.sl<TasksBloc>()),
        BlocProvider(create: (_) => di.sl<PomodoroBloc>()),
        BlocProvider(create: (_) => di.sl<AnalyticsBloc>()),
        BlocProvider(create: (_) => di.sl<StoreBloc>()),
      ],
      child: MaterialApp.router(
        title: 'FocusForge',
        theme: AppTheme.darkTheme,
        routerConfig: AppRouter.router,
        debugShowCheckedModeBanner: false,
      ),
    );
  }
}
